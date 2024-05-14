import pandas as pd
import numpy as np
import requests

import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession, Part
import vertexai.preview.generative_models as generative_models

import geopandas as gpd
from shapely.geometry import Point

import warnings
warnings.filterwarnings('ignore')


def fetch_data_if_chicago(search_filter, url, headers):
    """
    Checks if the 'location' field of the property information ends with 'chicago, il'.
    If it does, makes an API call to the specified URL with the given headers and querystring.
    Otherwise, recommends the main Zillow site.

    Parameters:
    - search_filter: dictionary of query parameters for the request
    - url: API endpoint URL
    - headers: dictionary of HTTP headers for the request
    
    Returns:
    - The response object if the location is in Chicago, otherwise None.
    """
    try:
        location = search_filter['location']
        if not location.lower().endswith('chicago, il'):
            print("Sorry, my specialty is in the Chicago area. If you are looking for a property in a different city, please refer to: https://www.zillow.com/")
            return None
        else:
            response = requests.get(url, headers=headers, params=search_filter)
            return response
    except KeyError:
        print("Error: 'location' field is missing from the property information.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_properties(response, n, fields):
    """
    Extracts and returns the top 'n' properties from a given API response
    based on the specified fields, appending the base URL to 'detailUrl'.
    
    Parameters:
    - response: The response object from an API call.
    - n: The number of top properties to extract.
    - fields: A list of strings representing the fields to extract from each property.
    
    Returns:
    - A list of dictionaries, each representing a property with only the specified fields.
    """
    base_url = "https://www.zillow.com"
    try:
        # Convert the response to JSON format if it's not already a dictionary
        if not isinstance(response, dict):
            response = response.json()

        # Extract the top 'n' properties based on the specified fields
        top_properties = []
        for prop in response['props'][:n]:
            extracted_prop = {field: (base_url + prop['detailUrl'] if field == 'detailUrl' else prop.get(field, None)) for field in fields}
            top_properties.append(extracted_prop)

        return top_properties

    except Exception as e:
        print("An error occurred:", e)
        return []  # Return an empty list in case of an error


def fetch_descriptions(properties):
    """
    Fetches the descriptions of each property and appends them to the list.

    Parameters:
    - properties: A list of dictionaries representing properties.

    Returns:
    - A list of dictionaries(the same format as input).
    """
    url_details = "https://zillow-com1.p.rapidapi.com/property"

    for prop in properties:
        # Fetch detailed information using detailUrl
        querystring = {"property_url": prop['detailUrl']}
        response = requests.get(url_details, headers=headers, params=querystring)

        # Convert to JSON and fetch description
        detail_data = response.json()
        prop['description'] = detail_data.get('description', 'No description available')

    return properties

def fetch_resoFacts(properties, headers, keys_to_fetch):
    """
    Fetches specific information from the resoFacts dictionary of each property and appends it in a nested format.

    Parameters:
    - properties: A list of dictionaries representing properties.
    - headers: Headers for the API request.
    - keys_to_fetch: A list of keys to fetch from the resoFacts dictionary.

    Returns:
    - A list of dictionaries with the specified information appended in a nested format.
    """
    url_details = "https://zillow-com1.p.rapidapi.com/property"

    for prop in properties:
        # Fetch detailed information using detailUrl
        querystring = {"property_url": prop['detailUrl']}
        response = requests.get(url_details, headers=headers, params=querystring)
        detail_data = response.json()

        # Fetch information from the resoFacts dictionary
        resoFacts = detail_data.get('resoFacts', {})

        # Create a nested dictionary to store resoFacts information
        prop['resoFacts'] = {}

        for key in keys_to_fetch:
            prop['resoFacts'][key] = resoFacts.get(key, 'N/A')

    return properties

def fetch_schools(properties, headers):
    """
    Fetches information about nearby schools and appends it in a nested format.

    Parameters:
    - properties: A list of dictionaries representing properties.
    - headers: Headers for the API request.

    Returns:
    - A list of dictionaries with school information appended in a nested format.
    """
    url_details = "https://zillow-com1.p.rapidapi.com/property"

    for prop in properties:
        # Fetch detailed information using detailUrl
        querystring = {"property_url": prop['detailUrl']}
        response = requests.get(url_details, headers=headers, params=querystring)
        detail_data = response.json()

        # Fetch schools information
        schools = detail_data.get('schools', [])

        # Create a nested dictionary to store school information
        prop['schools'] = schools

    return properties

def merge_property_and_restaurant_info(properties, restaurants):
    """
    Merges each property with its corresponding top-rated restaurants.

    Parameters:
    - properties: A list of dictionaries, each representing a property.
    - restaurants: A list of dictionaries, each representing top-rated restaurants near the properties.

    Returns:
    - A list of dictionaries, each representing a property merged with restaurant information.
    """
    # Ensure there are two restaurants for each property, assuming a structure of 1:2 mapping
    if len(restaurants) != 2 * len(properties):
        raise ValueError("Each property must correspond to exactly two restaurants.")

    merged_data = []
    for i, property in enumerate(properties):
        # Merge the property dict with its corresponding restaurants' info
        restaurant_info = {
            "restaurant_1": restaurants[2*i],
            "restaurant_2": restaurants[2*i + 1]
        }
        # Merge two dictionaries and add to the list
        merged_property = {**property, **restaurant_info}
        merged_data.append(merged_property)

    return merged_data

def load_neighborhood_boundaries(neighborhood_boundaries_path):
    neighborhoods = gpd.read_file(neighborhood_boundaries_path)
    return neighborhoods

def load_neighborhood_info(neighborhood_info_path):
    neighborhood_info = pd.read_csv(neighborhood_info_path)       
    return neighborhood_info

def fetch_neighborhood(top_properties, neighborhoods):
    for i in range(0, 3):
        latitude = top_properties[i]['latitude']
        longitude = top_properties[i]['longitude']
        point = gpd.GeoDataFrame([{'geometry': Point(longitude, latitude)}], crs='EPSG:4326')
        point = point.to_crs(neighborhoods.crs)
        point_in_neighborhood = gpd.sjoin(point, neighborhoods, how="inner", op='intersects')
        neighborhood = point_in_neighborhood['pri_neigh'].values[0]
        top_properties[i]['neighborhood'] = neighborhood
    return top_properties

def fetch_neighborhood_info(top_properties, neighborhood_info):
    neighborhood_info['neighborhood'] = neighborhood_info['neighborhood'].str.upper()
    for i in range(0, 3):
        neighborhood = top_properties[i]['neighborhood']
        try:
            neighborhood_description = neighborhood_info[neighborhood_info['neighborhood'] == neighborhood]['neighborhood_information'].values[0]
        except:
            neighborhood_description = 'Neighborhood description is not found.'
        top_properties[i]['neighborhood_description'] = neighborhood_description
    return top_properties

