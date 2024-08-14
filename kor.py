from kor import create_extraction_chain, Object, Text
from langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key="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",
    model_name="llama3-70b-8192",
    temperature=0,
    max_tokens=2000,
    model_kwargs={"frequency_penalty": 0, "presence_penalty": 0, "top_p": 1.0},
)

schema = Object(
    id="company",
    description=(
        "Extract information related to companies, including company name and a description containing all related data."
    ),
    attributes=[
        Text(
            id="company_name",
            description="The name of the company.",
            examples=[
                (
                    "Sanbrains Era Technologies Pvt Ltd Description: Specializes in a wide array of digital marketing services including SEO services, PPC services, social media marketing services, email marketing services, mobile app, and web development services. Known for mapping strategies, building brands, and elevating product experiences with quality engagements and SEO services. Location: Hyderabad Budget: The context does not specify exact pricing for Sanbrains, but given the range mentioned for digital marketing services (Rs 25,000 to Rs 2.5 Lakhs), a budget of 40,000 Rs could potentially be accommodated for a specific package or service. Timeline: The information does not explicitly mention timelines, but a one-month project could be feasible based on the services offered.",
                    "Sanbrains Era Technologies Pvt Ltd",
                ),
                (
                    "ITinfo Digital Description: Over 15 years of industry experience with a team of certified professionals. Known as one of the top digital marketing agencies in Hyderabad. Location: Hyderabad Budget: The cost range for their services is mentioned (Rs 25,000 to Rs 2.5 Lakhs), so a budget of 40,000 Rs is within this range. Timeline: Similar to Sanbrains, specific timelines are not mentioned, but they likely offer packages or services that can fit within a one-month duration.",
                    "ITinfo Digital",
                ),
            ],
        ),
        Text(
            id="description",
            description="All remaining data related to the company. like description, location, budget etc",
            examples=[
                (
                    "Sanbrains Era Technologies Pvt Ltd Description: Specializes in a wide array of digital marketing services including SEO services, PPC services, social media marketing services, email marketing services, mobile app, and web development services. Known for mapping strategies, building brands, and elevating product experiences with quality engagements and SEO services. Location: Hyderabad Budget: The context does not specify exact pricing for Sanbrains, but given the range mentioned for digital marketing services (Rs 25,000 to Rs 2.5 Lakhs), a budget of 40,000 Rs could potentially be accommodated for a specific package or service. Timeline: The information does not explicitly mention timelines, but a one-month project could be feasible based on the services offered.",
                    "Specializes in a wide array of digital marketing services including SEO services, PPC services, social media marketing services, email marketing services, mobile app, and web development services. Known for mapping strategies, building brands, and elevating product experiences with quality engagements and SEO services. Location: Hyderabad Budget: The context does not specify exact pricing for Sanbrains, but given the range mentioned for digital marketing services (Rs 25,000 to Rs 2.5 Lakhs), a budget of 40,000 Rs could potentially be accommodated for a specific package or service. Timeline: The information does not explicitly mention timelines, but a one-month project could be feasible based on the services offered.",
                ),
                (
                    "ITinfo Digital Description: Over 15 years of industry experience with a team of certified professionals. Known as one of the top digital marketing agencies in Hyderabad. Location: Hyderabad Budget: The cost range for their services is mentioned (Rs 25,000 to Rs 2.5 Lakhs), so a budget of 40,000 Rs is within this range. Timeline: Similar to Sanbrains, specific timelines are not mentioned, but they likely offer packages or services that can fit within a one-month duration.",
                    "Over 15 years of industry experience with a team of certified professionals. Known as one of the top digital marketing agencies in Hyderabad. Location: Hyderabad Budget: The cost range for their services is mentioned (Rs 25,000 to Rs 2.5 Lakhs), so a budget of 40,000 Rs is within this range. Timeline: Similar to Sanbrains, specific timelines are not mentioned, but they likely offer packages or services that can fit within a one-month duration.",
                ),
            ],
        ),
    ],
    many=True,
)


chain = create_extraction_chain(llm, schema, encoder_or_encoder_class="json")
data = chain.invoke(
    """
Based on the provided context, here are the companies that match the specified criteria for SEO services with a budget of 10000Rs, a timeline of 1 month, and located in Kolkata:

    Indian SEO Company
        Description: Specializes in SEO services.
        Location: Y8, EP Block, Sector V, Salt Lake City, Kolkata, West Bengal, 700091.
        Budget and Timeline: While the exact budget and timeline are not explicitly mentioned in the context, the company emphasizes not burning a hole in the client's pocket, which suggests affordability. The company’s focus on small businesses also implies they might be willing to work within a budget of 10000Rs and a timeline of 1 month.

    Ecom Buzz
        Description: Provides SEO services among other digital marketing services.
        Location: P 707 lake town block a, Kolkata, West Bengal, 700089.
        Budget and Timeline: Charges are less than $25/hr, which can be within the budget of 10000Rs for a month-long project. The company has a high rating and positive review from a client, indicating their competency and reliability.

Rational and Logic:

    Indian SEO Company:
        Specialization: Clearly focused on SEO services, as mentioned in their capabilities and specialities.
        Location: Based in Kolkata, fitting the location requirement.
        Cost: Emphasizes affordability, likely aligning with the budget constraint of 10000Rs.

    Ecom Buzz:
        Specialization: Offers SEO services as part of their digital marketing portfolio.
        Location: Based in Kolkata, meeting the location requirement.
        Cost: With rates explicitly mentioned as < $25/hr, it is feasible to fit within the 10000Rs budget for a month-long engagement.

Thanks for asking!

"""
)
companies = data["data"]["company"]
print(companies)
print()
for company in companies:
    keys = company.keys()
    for key in keys:
        print(f"{key}: {company[key]}")
    print()
