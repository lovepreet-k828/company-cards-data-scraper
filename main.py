import os
import re
import json
import random
import asyncio
from pathlib import Path
from pyppeteer import launch
from bs4 import BeautifulSoup


async def fetch_page(url, selector=None):
    """
    Fetches the content of a web page using a headless browser.

    Args:
        url (str): The URL of the web page to fetch.

    Returns:
        str: The content of the web page, or None if an error occurs.
    """
    # Launch a headless browser
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()

    # Set a random user-agent to mimic a real browser request
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    ]
    user_agent = random.choice(user_agents)
    await page.setUserAgent(user_agent)

    # Enable cookies and set the referer header
    await page.setExtraHTTPHeaders(
        {
            "Referer": "https://www.google.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
    )

    try:
        # Go to the URL and wait for the network to be idle
        await page.goto(url, {"waitUntil": "networkidle2", "timeout": 100000})
        # Wait for an additional 10 seconds
        if selector:
            await page.waitForSelector(selector, {"timeout": 100000})
        content = await page.content()
    except Exception as e:
        # Handle any errors that occur during the page fetch
        print(f"Error fetching page {url}: {e}")
        content = None
    finally:
        # Close the browser
        await browser.close()

    # Check if HTML is not correctly fetched
    if content == None or "Enable JavaScript and cookies to continue" in content:
        print(f"Failed to fetch HTML content from {url}\n user_agent: {user_agent}")
        return None

    return content


def get_sanitized_file_name(file_name):
    """
    Sanitize a file name by replacing special characters with underscores and spaces with underscores.

    Args:
        file_name (str): The original file name to be sanitized.

    Returns:
        str: The sanitized file name.
    """
    # Replace any character that is not a word character, whitespace, or hyphen with an underscore
    sanitized_name = re.sub(r"[^\w\s-]", "_", file_name)

    # Replace spaces with underscores
    sanitized_name = sanitized_name.replace(" ", "_")

    return sanitized_name


async def save_html_content(directory, company_name, url, failure_retries):
    """
    Fetches the HTML content of a page and saves it to a file.

    Args:
        directory (str): The directory where the HTML file will be saved.
        company_name (str): The name of the company, used to name the HTML file.
        url (str): The URL of the page to fetch.

    Returns:
        str: The HTML content of the page if fetched successfully, otherwise None.
    """
    # Create a sanitized file name by replacing special characters in company_name with underscores
    sanitized_file_name = get_sanitized_file_name(company_name)

    # Construct the file path
    file_path = f"{directory}/{sanitized_file_name}.html"
    html_content = None
    while html_content == None and failure_retries > 0:
        html_content = await fetch_page(url)
    if not html_content:
        return

    # Save the fetched HTML content to a file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"Successfully saved HTML content for {company_name} from {url}")

    return html_content


def extract_company_info(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract company logo URL
    logo_tag = soup.find(
        "a", class_="profile-header__logotype sg-provider-logotype website-link__item"
    ).find("img")
    logo_url = logo_tag["src"] if logo_tag else None

    # Extract company name
    name_tag = soup.find("h1", class_="profile-header__title")
    company_name = name_tag.get_text(strip=True) if name_tag else None

    # Extract company summary
    summary_div = soup.find("div", id="profile-summary-text")
    summary_paragraphs = summary_div.find_all("p") if summary_div else []
    company_summary = " ".join([p.get_text(strip=True) for p in summary_paragraphs])

    # Extract details from the list
    details_list = soup.find("ul", class_="profile-summary__details")
    details_info = {}
    if details_list:
        for detail in details_list.find_all("li", class_="profile-summary__detail"):
            label = detail.get("data-tooltip-content", "").strip("<i>").strip("</i>")
            value = detail.find("span", class_="sg-text__title")
            if value:
                value = value.get_text(strip=True)

            if label == "Min. project size":
                details_info["min_project_size"] = value
            elif label == "Avg. hourly rate":
                details_info["avg_hourly_rate"] = value
            elif label == "Employees":
                details_info["employee_count"] = value
            elif label == "Location":
                details_info["location"] = value
            elif label == "Founded":
                details_info["founded_date"] = value
    else:
        details_info = {}

    # Create a dictionary with all extracted information
    company_info = {
        "logo_url": logo_url,
        "company_name": company_name,
        "company_summary": company_summary,
        **details_info,
    }

    return company_info


def save_to_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


async def save_json_content(directory, company_name, url):
    base_path = Path(__file__).resolve().parent
    Path(f"{base_path}/{directory}/html").mkdir(parents=True, exist_ok=True)
    Path(f"{base_path}/{directory}/json").mkdir(parents=True, exist_ok=True)
    json_filename = f"{get_sanitized_file_name(company_name)}.json"

    if os.path.exists(f"{directory}/json/{json_filename}"):
        return

    html_content = await save_html_content(
        directory=f"{directory}/html",
        company_name=company_name,
        url=url,
        failure_retries=3,
    )

    if not html_content:
        print(f"Error: Failed to fetch url: {url}")
        return

    # Extract information
    company_info = extract_company_info(html_content)

    # Save to JSON file
    save_to_json(company_info, f"{directory}/json/{json_filename}")

    print(f"Data successfully extracted and saved to {json_filename}")


async def main():
    with open("clutch_profile_links.json", "r") as json_file:
        data = json.load(json_file)

    # Process each company in the JSON data
    for company in data["companies"]:
        company_name = company["name"]
        clutch_profile_url = company["view_profile_url"]

        try:
            await save_json_content(
                directory="scrapped_data_company_info_cards",
                company_name=company_name,
                url=clutch_profile_url,
            )
        except Exception as e:
            print(f"Error occured for {company_name}: {e}")


asyncio.run(main())
