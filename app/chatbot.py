import os
from property_info import extract_json_to_dict, fetch_top_properties_detail
from neighborhood import get_neighborhood_details
from property_info import extract_json_to_dict, fetch_top_properties_detail
from map_creation import create_property_map, create_local_advisor_map
from local_advisor import generate_local_search_query, search_google_places, generate_local_advisor_response
from yelp import (
    yelp_advisor,
    fetch_top_businesses_near_properties,
    extract_business_info,
    merge_property_and_restaurant_info
)
from prompt_creation import (
    generate_prompt_classifier,
    generate_prompt_property,
    generate_prompt_apifilter,
    generate_prompt_rag_neighborhood,
    generate_prompt_yelp_advisor,
    final_output_yelp_advisor,
    generate_prompt_rag_international,
    generate_prompt_general,
    generate_prompt_rewrite_query,
    generate_prompt_local_advisor
)
from llm import get_chat_response
from rag import get_context, reciprocal_rank_fusion
from vector_search import search_similar_chunks, format_chunk_results
import json

GOOGLE_MAPS_API_KEY = os.getenv("DEV_GOOGLE_MAP_API_KEY")

# initial intent
def intent_classifier(chat, prompts_dict, user_query):
    prompt = generate_prompt_classifier(prompts_dict['instruction_classifier'], user_query)
    response = get_chat_response(chat, prompt)
    print('Intent Number:', int(response))
    return int(response)


# functions for property search
def get_listings_from_zillow(chat, prompts_dict, user_query):
    prompt = generate_prompt_apifilter(prompts_dict['instruction_apifilter'], user_query, locations_string = prompts_dict['zillow_locations'])
    api_filter = get_chat_response(chat, prompt)
    api_filter = extract_json_to_dict(api_filter)
    top_properties = fetch_top_properties_detail(api_filter)
    return top_properties


def get_top_restaurants_yelp(chat, prompts_dict, user_query, top_properties):
    categories = prompts_dict['yelp_categories']
    yelp_results = fetch_top_businesses_near_properties(
        properties=top_properties,
        user_query=user_query,
        categories=categories,
        chat=chat,
        prompts_dict=prompts_dict
    )
    top_restaurants = extract_business_info(yelp_results)
    return top_restaurants
    

def get_final_respone_property(chat, prompts_dict, user_query, property_info):
    prompt = generate_prompt_property(prompts_dict['instruction_property_final'], user_query, property_info)
    response = get_chat_response(chat, prompt)
    return response
    

def chat_property(chat, prompts_dict, user_query, neighborhoods_info, neighborhoods_boundaries):
    top_properties = get_listings_from_zillow(chat, prompts_dict, user_query)
    print('Top properties:', top_properties)
    
    # Case1: Add Yelp and neighborhood information to the properties   
    # top_restaurants = get_top_restaurants_yelp(chat, prompts_dict, user_query, top_properties)
    # print('Top Restaurants:', top_restaurants)
    # top_properties_and_restaurants = merge_property_and_restaurant_info(top_properties, top_restaurants)
    # print('Top properties and restaurants:', top_properties_and_restaurants)
    # property_info_final = get_neighborhood_details(
    #     top_properties=top_properties_and_restaurants,
    #     neighborhoods_info=neighborhoods_info,
    #     neighborhoods_boundaries=neighborhoods_boundaries
    # )
    # print('Top properties and restaurants with Neighborhood info:', property_info_final)
    # response_property_final = get_final_respone_property(chat, prompts_dict, user_query, property_info=property_info_final)
    
    # Case2: Use only properties information
    property_info_final = top_properties
    response_property_final = get_final_respone_property(chat, prompts_dict, user_query, property_info=property_info_final)

    # Generate the property map
    map_html = create_property_map(api_key=GOOGLE_MAPS_API_KEY, top_properties=top_properties)
    
    return response_property_final, map_html


# functions for restaurant search
def chat_yelp(chat, prompts_dict, user_query):
    categories_string = prompts_dict['yelp_categories']
    yelp_prompt = generate_prompt_yelp_advisor(prompts_dict['yelp_advisor_instructions'], user_query, categories_string)
    yelp_filter_str = get_chat_response(chat, yelp_prompt)
    yelp_filter = extract_json_to_dict(yelp_filter_str)
    yelp_advisor_results = yelp_advisor(yelp_filter)
    print('Yelp Info:', yelp_advisor_results)
    yelp_output_prompt = final_output_yelp_advisor(prompts_dict['yelp_output_instructions'], user_query, yelp_advisor_results)
    response_restaurant_final = get_chat_response(chat, yelp_output_prompt)
    return response_restaurant_final


# functions for neighborhood information
# def chat_neighborhood(chat, prompts_dict, user_query, vector_store):
#     context = get_context(user_query, vector_store)
#     print('Context:', context)
#     prompt_rag_neighborhood = generate_prompt_rag_neighborhood(prompts_dict['instruction_rag_neighborhood'], context, user_query)
#     response_neighborhood_final = get_chat_response(chat, prompt_rag_neighborhood)
#     return response_neighborhood_final


def rewrite_queries(chat, prompts_dict, user_query):
    prompt_rewrite_query = generate_prompt_rewrite_query(prompts_dict['instruction_rewrite_query'], user_query)
    response_rewrite_query = get_chat_response(chat, prompt_rewrite_query)
    print("Original Response from Rewrite Queries:", response_rewrite_query)

    try:
        # Attempt to parse the response content as JSON list
        result = json.loads(response_rewrite_query)

        # Check if result is a list and contains the original question and rewrites
        if isinstance(result, list) and user_query in result:
            return result
        else:
            # Return original question if parsing fails
            return [user_query]
    except (json.JSONDecodeError, AttributeError):
        # Return original question if there's an error
        return [user_query]


# functions for international students
def chat_international(chat, prompts_dict, user_query, vectordb, fusion=False):

    if fusion:
        rewritten_queries = rewrite_queries(chat, prompts_dict, user_query)
        all_results = []
        for query in rewritten_queries:
            chunks = search_similar_chunks(vectorstore=vectordb, query=query, k=5)
            all_results.append(chunks)
        chunks = reciprocal_rank_fusion(all_results, top_n=5)
    else:
        chunks = search_similar_chunks(vectorstore=vectordb, query=user_query, k=5)
    
    chunks_formated = format_chunk_results(
            chunks,
            metadata_fields=['source', 'source_type'],
            include_content=True
            )
    # print('Contexts:', chunks_formated)
    prompt_rag_international = generate_prompt_rag_international(prompts_dict['instruction_rag_international'], chunks_formated, user_query)
    response_international_final = get_chat_response(chat, prompt_rag_international)
    return response_international_final


# functions for general response
def chat_general(chat, prompts_dict, user_query):
    prompt_general = generate_prompt_general(prompts_dict['instruction_general'], user_query)
    response_general_final = get_chat_response(chat, prompt_general)
    return response_general_final


def chat_local_advisor(chat, prompts_dict, user_query, api_key):
    """
    Handles Local Advisor user queries by refining the query, performing the Google Places search,
    and generating a response.

    Args:
        chat (object): LLM chat instance.
        prompts_dict (dict): Dictionary containing prompts.
        user_query (str): The user's query.
        api_key (str): Google Maps API key.

    Returns:
        tuple: Response text and map HTML.
    """
    # Step 1: Refine the user's query with LLM
    instruction = prompts_dict["instruction_local_advisor"]
    refined_query = generate_local_search_query(chat, instruction, user_query)

    search_string = refined_query["search_string"]
    included_type = refined_query["included_type"]

    # Step 2: Perform the Google Places Text Search
    places = search_google_places(api_key, search_string, included_type)

    # Step 3: Generate a response for the user using LLM
    if places:
        response_instruction = prompts_dict["instruction_local_advisor_response"]
        response = generate_local_advisor_response(chat, response_instruction, user_query, places)
    else:
        response = f"Sorry, I couldn't find any results for '{search_string}'."

    # Step 4: Generate the map HTML
    map_html = create_local_advisor_map(api_key, places)

    return response, map_html


# final
def chat_all(chat, prompts_dict, user_query, neighborhoods_info, neighborhoods_boundaries, vectordb):
    
    intent_int = intent_classifier(chat, prompts_dict, user_query)

    if intent_int == 1:  # Property intent
        response_property_final, map_html = chat_property(chat, prompts_dict, user_query, neighborhoods_info, neighborhoods_boundaries)
        return response_property_final, map_html, intent_int
    elif intent_int == 2:  # Local Advisor intent
        response_local_advisor, map_html = chat_local_advisor(chat, prompts_dict, user_query, GOOGLE_MAPS_API_KEY)
        return response_local_advisor, map_html, intent_int
    elif intent_int == 3:  # International Student Advisor intent
        response_international_final = chat_international(chat, prompts_dict, user_query, vectordb, fusion=True)
        return response_international_final, None, intent_int
    else:   # Other intent
        response_default = chat_general(chat, prompts_dict, user_query)
        return response_default, None, intent_int
