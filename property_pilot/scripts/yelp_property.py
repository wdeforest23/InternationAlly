# Importing required libraries
import pandas as pd
import numpy as np
import os
import http.client
import json
import urllib.parse
import warnings
warnings.filterwarnings('ignore')

import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, Part
import vertexai.preview.generative_models as generative_models

def get_chat_response(chat: ChatSession, prompt: str) -> str:
    text_response = []
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

def generate_prompt_rest_category(user_query, categories):      
    # Format the list into a single string separated by commas for the model
    categories_string = ','.join(categories)
    
    instruction = f"""
    ### Instructions ###
    Identify the category of restaurant the user is interested in based on their query. 
    If the query doesn't specify a category, return "restaurants".
    Your output should be a lowercase string. 
    If there are multiple categories, separate them with a comma.
    There should be NO WHITE SPACES OR NEW LINE CHARACTERS.
    
    ### Possible Categories ###
    {categories_string}

    ### User’s query ###
    {user_query}

    ### Output ###
    """
    return instruction

def get_top_rated_businesses(api_key, location, category, top_n=2):
    """Fetches top-rated businesses near a given location from Yelp."""
    conn = http.client.HTTPSConnection("api.yelp.com")
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    params = {
        'location': location,
        'term': 'restaurants',
        'radius': 2000,
        'categories': category,
        'sort_by': 'rating',
        'limit': top_n
    }
    
    # Encode parameters into URL query string
    query_string = urllib.parse.urlencode(params)
    url = f"/v3/businesses/search?{query_string}"
    
    conn.request("GET", url, headers=headers)
    
    response = conn.getresponse()
    data = response.read()
    conn.close()
    
    if response.status == 200:
        return json.loads(data)
    else:
        print(f"Failed to fetch data: {response.status} - {data.decode('utf-8')}")
        return None  # Handle the failure as appropriate in your application

def fetch_top_businesses_near_properties(api_key, properties, user_query, categories, chat):
    """
    Fetches top-rated businesses of a specified category near each property in a given list,
    using a category inferred from a user query processed by Gemini LLM.
    """
    prompt = generate_prompt_rest_category(user_query, categories)
    category = get_chat_response(chat, prompt)  # Get the category from the LLM
    category = category.strip().replace('"', '')  # Strip any quotation marks or white space from the category
    if not category or category.lower() == "restaurants":
        category = "restaurants"  # default to 'restaurants' if no specific category identified

    top_restaurants_yelp = []
    for property in properties:
        location = f"{property['latitude']}, {property['longitude']}"
        top_businesses = get_top_rated_businesses(api_key, location, category)
        top_restaurants_yelp.append({
            'address': property['address'],
            'top_businesses': top_businesses
        })
    
    return top_restaurants_yelp

def extract_business_info(addresses, n, fields):
    """
    Extracts and returns information from a given list of addresses, each containing businesses,
    based on the specified fields and the top 'n' businesses per address.
    
    Parameters:
    - addresses: A list of dictionaries, each representing an address with nested businesses.
    - n: The number of top businesses to extract from each address.
    - fields: A list of strings representing the fields to extract from each business.
    
    Returns:
    - A list of dictionaries, each representing a business with only the specified fields.
    """
    extracted_businesses = []
    try:
        # Loop through each address entry
        for address_entry in addresses:
            # Extract top 'n' businesses
            for business in address_entry['top_businesses']['businesses'][:n]:
                # Extract specified fields, handling nested structures like 'categories' and 'location'
                extracted_business = {
                    'business_name': business.get('name'),
                    'categories_titles': [category['title'] for category in business.get('categories', [])],
                    'rating': business.get('rating'),
                    'latitude': business.get('coordinates', {}).get('latitude'),
                    'longitude': business.get('coordinates', {}).get('longitude'),
                    'display_address': " ".join(business.get('location', {}).get('display_address', [])),
                    'url': business.get('url')
                }
                # Only append fields that were specifically requested
                filtered_business = {field: extracted_business[field] for field in fields if field in extracted_business}
                extracted_businesses.append(filtered_business)

        return extracted_businesses

    except Exception as e:
        print("An error occurred:", e)
        return []  # Return an empty list in case of an error


