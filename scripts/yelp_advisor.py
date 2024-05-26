# Importing required libraries
import pandas as pd
import numpy as np
import os
import http.client
from typing import Dict, Any
import folium
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

# Function to generate the Yelp API filter parameters based on user query
def generate_prompt_yelp_advisor(yelp_advisor_instruction, user_query, categories_string):
    prompt = yelp_advisor_instruction.replace("{USER_QUERY}", user_query)
    prompt = prompt.replace("{CATEGORIES_STRING}", categories_string)
    return prompt

#Function to call the Yelp API
def yelp_advisor(api_key: str, yelp_filter: Dict[str, Any]):
    """Fetches top-rated businesses near a given location from Yelp."""
    conn = http.client.HTTPSConnection("api.yelp.com")
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    params = yelp_filter
    #print(params)
    
    # Encode parameters into URL query string
    query_string = urllib.parse.urlencode(params, doseq=True)
    #print(query_string)
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

def create_yelp_restaurant_map(yelp_advisor_results):
    # Attribution for custom tileset
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    
    # Initialize the map centered around Chicago
    restaurant_map = folium.Map(location=[41.881832, -87.623177], zoom_start=11, tiles='OpenStreetMap', attr=attr)

    # Loop through each business in the Yelp results
    for business in yelp_advisor_results['businesses']:
        # Extract restaurant details
        name = business['name']
        categories = ', '.join([category['title'] for category in business['categories']])
        rating = business['rating']
        latitude = business['coordinates']['latitude']
        longitude = business['coordinates']['longitude']
        address = ', '.join(business['location']['display_address'])
        url = business['url']
        
        # Add a marker to the map for the restaurant
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(f'<a href="{url}" target="_blank">{name}</a><br/>{categories}<br/>Rating: {rating}<br/>{address}', max_width=250),
            tooltip=f"Click for details on {name}",
            icon=folium.Icon(icon='cutlery', color="red")
        ).add_to(restaurant_map)

    # Return the map
    return restaurant_map

def final_output_yelp_advisor(output_instructions, user_query, yelp_advisor_results):
    updated_instruction = output_instructions.replace("{USER_QUERY}", user_query)
    updated_instruction = updated_instruction.replace("{YELP_RESULTS}", str(yelp_advisor_results))
    return updated_instruction
