# Importing required libraries
import pandas as pd
import numpy as np
import folium
import warnings
warnings.filterwarnings('ignore')

def create_property_map(properties):
    # Attribution for custom tileset
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    
    # Initialize the map centered around Chicago
    property_map = folium.Map(location=[41.881832, -87.623177], zoom_start=11, tiles='OpenStreetMap_Mapnik', attr=attr)

    # Loop through each property in the list
    for prop in properties:
        # Extract latitude and longitude
        latitude = prop['latitude']
        longitude = prop['longitude']
        detail_url = prop['detailUrl']
        address = prop['address']

        # Add markers to the map
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(f'<a href="{detail_url}" target="_blank">{address}</a>', max_width=250),
            tooltip="Click for Zillow Listing",
            icon=folium.Icon(icon = 'home', color="blue")
        ).add_to(property_map)
    return property_map

def create_property_restaurant_map(properties):
    # Attribution for custom tileset
    attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    
    # Initialize the map centered around Chicago
    property_map = folium.Map(location=[41.881832, -87.623177], zoom_start=11, tiles='OpenStreetMap', attr=attr)

    # Loop through each property location in the list
    for prop in properties:
        # Extract property details
        latitude = prop['latitude']
        longitude = prop['longitude']
        detail_url = prop['detailUrl']
        address = prop['address']

        # Add a marker to the map for the property
        folium.Marker(
            location=[latitude, longitude],
            popup=folium.Popup(f'<a href="{detail_url}" target="_blank">{address}</a>', max_width=250),
            tooltip="Click for property details",
            icon=folium.Icon(icon='home', color="blue")
        ).add_to(property_map)

        # Loop through the associated restaurants
        for key in ['restaurant_1', 'restaurant_2']:
            if key in prop:
                restaurant = prop[key]
                # Extract relevant restaurant data
                name = restaurant['business_name']
                categories = ', '.join(restaurant['categories_titles'])
                rating = restaurant['rating']
                res_latitude = restaurant['latitude']
                res_longitude = restaurant['longitude']
                res_address = restaurant['display_address']
                url = restaurant['url']

                # Add a marker to the map for the restaurant
                folium.Marker(
                    location=[res_latitude, res_longitude],
                    popup=folium.Popup(f'<a href="{url}" target="_blank">{name}</a><br/>{categories}<br/>Rating: {rating}', max_width=250),
                    tooltip=f"Click for details on {name}",
                    icon=folium.Icon(icon='cutlery', color="red")
                ).add_to(property_map)
    return property_map

def generate_prompt_property(instruction, user_query, property_info, fields):
    '''
    user_query: user's original query
    property_info :property info, including all detailed information
    fields: key info to be included in the answer from LLM, even if user's query does not specify it
    '''
    
    updated_instruction = instruction.replace("{USER_QUERY}", user_query)
    updated_instruction = updated_instruction.replace("{PROPERTY_INFO}", property_info)
    updated_instruction = updated_instruction.replace("{KEY_FIELDS}", fields)
    return updated_instruction

# Function to make property info to readable format
def format_properties(properties, fields):
    formatted_properties = []
    for prop in properties:
        # Format and concatenate each field of each property
        formatted_prop = ', '.join(f"{field.capitalize().replace('_', ' ')}: {prop.get(field, 'N/A')}" for field in fields)
        formatted_properties.append(formatted_prop)
    return '\n\n'.join(formatted_properties)

def generate_prompt_classifier(instruction, user_query):
    return instruction.replace("{USER_QUERY}", user_query)
