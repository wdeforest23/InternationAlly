# Welcome to PropertyPilot!

PropertyPilot is an AI-powered real estate assistant designed to transform the home-buying process. This innovative tool is being developed by a dedicated team of University of Chicago Applied Data Science Master’s students: Kshitiz Sahay, Daichi Ishikawa, Yijing Sun, and William DeForest. Our project is part of the Conversational AI Research Capstone Course, advised by Nick Kadochnikov and Egehan Yorulmaz. Work on PropertyPilot began in March 2024, and what you see now is the result of a single quarter's effort. We’re taking a break for the summer, but we'll be back in Fall 2024 to continue refining and expanding our project.

![UI](images/ui_sample.png)

## Background and Motivation

The real estate sales and brokerage market, valued at over $200 billion, is undergoing significant change. Historically, real estate companies and agents dominated the home purchasing process, but platforms like Zillow and Redfin have democratized property searches, reducing the necessity for traditional real estate agents. While these platforms have simplified property searches, they have also diminished a key part of realtors' roles, leading to a recent settlement that officially eliminated high commissions.

Despite these changes, real estate agents still offer invaluable experience, expertise, and local knowledge that can provide buyers with the confidence and peace of mind needed during the often intimidating home-buying process. Moreover, while Zillow and Redfin have simplified property searches, users still need to switch between multiple platforms to search for related local information such as Yelp or Tripadvisor. Therefore, the existence of a conversational platform that consolidates all information in one place is highly valuable.

## Introducing PropertyPilot

We believe there’s a unique opportunity to revolutionize the home purchasing experience by integrating property search and real estate advice into one seamless platform, powered by large-language models (LLMs).

PropertyPilot combines state-of-the-art property searching capabilities with expert local market advice. Our natural language property search makes finding the perfect home simple and customizable. Additionally, PropertyPilot offers expert advice on a range of topics, from identifying the best neighborhoods and schools to recommending local restaurants, building budgets, and navigating the legal process—all of which fulfill the essential role of a human realtor.

In order to provide more detailed information, we plan to focus on Chicago initially.

## Key Features

- **Advanced Property Search:** Enables property searches using natural language. This is achieved by converting user free-form text into API filters for Zillow through multi-shot prompting.
- **Local Advice:** Allows users to inquire about local information related to the properties in the search results, such as schools, transportation, restaurants, and neighborhoods. This is realized by linking property location information with various local information sources.
- **Restaurant Recommendation:** Enables restaurant searches using natural language. This is achieved by converting user free-form text into API filters for Yelp through multi-shot prompting.
- **Expert Neighborhood Advisor:** Allows users to obtain detailed neighborhood information using natural language. This is accomplished by building a Retrieval-Augmented Generation (RAG) system using web-scraped content from Chicago neighborhood blogs.

## PropertyPilot Architecture

![architecture](images/architecture.png)

## Demo

TBU

## Next Steps

TBU

## Summary

PropertyPilot provides home buyers and sellers with a convenient, customizable, and cost-effective way to navigate the home purchasing process. Our platform empowers users by combining advanced technology with expert advice, ensuring a smooth and confident journey to finding the perfect home. Not only does PropertyPilot facilitate property searches, but it also offers comprehensive local information about Chicago, including insights on neighborhoods, schools, transportation, and restaurants, making it a truly all-encompassing tool for making informed decisions.

Stay tuned for more updates in the Fall of 2024!
