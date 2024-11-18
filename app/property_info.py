import json
import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import Point
import os
import requests
import time
from dotenv import load_dotenv
# load_dotenv()

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)


zillow_api = os.getenv("ZILLOW_API_KEY")
# Make a request to Zillow API
url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
url_details = "https://zillow-com1.p.rapidapi.com/property"

headers = {
    "X-RapidAPI-Key": zillow_api,
    "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
}


def extract_json_to_dict(text):
    """
    Extracts a JSON object from a string of text.

    :param text: str - The text containing a JSON object.
    :return: dict or str - The extracted JSON object as a dictionary, or an error message if the JSON is invalid.
    """
    start = text.find('{')
    end = text.rfind('}') + 1

    if start != -1 and end != -1:
        json_str = text[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return "Invalid JSON format"
    else:
        return "No valid JSON object found"


def fetch_data_if_chicago(search_filter, url=url, headers=headers):
    """
    Checks if the location is in Chicago and fetches data from the Zillow API if true.

    :param search_filter: dict - Query parameters for the API request.
    :param url: str - API endpoint URL.
    :param headers: dict - HTTP headers for the request.
    :return: Response object if successful, otherwise None.
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


def extract_properties(response, fields, n=5):
    """
    Extracts the top 'n' properties from the API response based on specified fields.
    Handles both standard property data and buildings with nested units.

    :param response: Response object or dict - The API response containing property data.
    :param n: int - The number of top properties to extract.
    :param fields: list - The fields to extract from each property.
    :return: list - A list of dictionaries, each representing a property with the specified fields.
    """
    base_url = "https://www.zillow.com"
    try:
        # Convert the response to JSON format if it's not already a dictionary
        if not isinstance(response, dict):
            response = response.json()

        # Extract properties
        top_properties = []
        for prop in response.get('props', []):
            # If the property is a building with units
            if prop.get('isBuilding') and 'units' in prop:
                for unit in prop['units']:
                    extracted_prop = {
                        'address': f"{prop.get('buildingName', 'Unknown Building')}, {prop.get('address', 'Unknown Address')}",
                        'price': unit.get('price'),
                        'bedrooms': unit.get('beds'),
                        'bathrooms': unit.get('baths', None),  # Units often lack bathrooms info
                        'detailUrl': base_url + prop.get('detailUrl', ''),
                        'imgSrc': prop.get('imgSrc', None),
                        'latitude': prop.get('latitude', None),
                        'longitude': prop.get('longitude', None),
                        'zpid': prop.get('zpid', None),
                    }
                    top_properties.append(extracted_prop)
            else:  # Standard property data
                extracted_prop = {
                    'address': prop.get('address', 'Unknown Address'),
                    'price': prop.get('price', None),
                    'bedrooms': prop.get('bedrooms', None),
                    'bathrooms': prop.get('bathrooms', None),
                    'detailUrl': base_url + prop.get('detailUrl', ''),
                    'imgSrc': prop.get('imgSrc', None),
                    'latitude': prop.get('latitude', None),
                    'longitude': prop.get('longitude', None),
                    'zpid': prop.get('zpid', None),
                }
                top_properties.append(extracted_prop)

            # Stop if we've collected 'n' properties
            if len(top_properties) >= n:
                break

        return top_properties[:n]

    except Exception as e:
        print("An error occurred:", e)
        return []  # Return an empty list in case of an error


def fetch_descriptions(properties, headers=headers, url_details=url_details):
    """
    Fetches and appends property descriptions from the API to the property list.

    :param properties: list - A list of dictionaries representing properties.
    :return: list - The updated list of properties with descriptions included.
    """
    for prop in properties:
        # Fetch detailed information using detailUrl
        querystring = {"property_url": prop['detailUrl']}
        response = requests.get(url_details, headers=headers, params=querystring)

        # Convert to JSON and fetch description
        detail_data = response.json()
        prop['description'] = detail_data.get('description', 'No description available')

    return properties


def fetch_resoFacts(properties, keys_to_fetch, headers=headers):
    """
    Fetches specific fields from the resoFacts section of each property and appends them.

    :param properties: list - A list of dictionaries representing properties.
    :param headers: dict - HTTP headers for the API request.
    :param keys_to_fetch: list - The specific keys to extract from the resoFacts dictionary.
    :return: list - The updated list of properties with the resoFacts information appended.
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


def fetch_schools(properties, headers=headers):
    """
    Fetches school information for each property and appends it to the list.

    :param properties: list - A list of dictionaries representing properties.
    :param headers: dict - HTTP headers for the API request.
    :return: list - The updated list of properties with nearby school information included.
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


def fetch_neighborhood(top_properties, neighborhoods):
    """
    Identifies and appends the neighborhood for each property based on its location.

    :param top_properties: list - A list of dictionaries representing properties.
    :param neighborhoods: GeoDataFrame - The GeoDataFrame containing neighborhood boundaries.
    :return: list - The updated list of properties with neighborhood information appended.
    """
    for i in range(0, len(top_properties)):
        latitude = top_properties[i]['latitude']
        longitude = top_properties[i]['longitude']
        point = gpd.GeoDataFrame([{'geometry': Point(longitude, latitude)}], crs='EPSG:4326')
        point = point.to_crs(neighborhoods.crs)
        point_in_neighborhood = gpd.sjoin(point, neighborhoods, how="inner", op='intersects')
        neighborhood = point_in_neighborhood['pri_neigh'].values[0]
        top_properties[i]['neighborhood'] = neighborhood
    return top_properties


def fetch_neighborhood_info(top_properties, neighborhood_info):
    """
    Appends neighborhood descriptions to each property.

    :param top_properties: list - A list of property dictionaries with neighborhood information.
    :param neighborhood_info: DataFrame - A DataFrame containing neighborhood descriptions.
    :return: list - The updated list of properties with neighborhood descriptions included.
    """
    neighborhood_info['neighborhood'] = neighborhood_info['neighborhood'].str.strip()
    for i in range(0, len(top_properties)):
        neighborhood = top_properties[i]['neighborhood']
        try:
            neighborhood_description = neighborhood_info[neighborhood_info['neighborhood'] == neighborhood]['neighborhood_information'].values[0]
        except:
            neighborhood_description = 'Neighborhood description is not found.'
        top_properties[i]['neighborhood_description'] = neighborhood_description
    return top_properties


# def format_properties(properties, fields):
#     """
#     Formats property information into a human-readable string based on specified fields.

#     :param properties: list - A list of dictionaries, each representing a property.
#     :param fields: list - A list of fields to be extracted and formatted from each property.
#     :return: str - A string with the formatted property details, with each property separated by a blank line.
#     """
#     formatted_properties = []
#     for prop in properties:
#         # Format and concatenate each field of each property
#         formatted_prop = ', '.join(f"{field.capitalize().replace('_', ' ')}: {prop.get(field, 'N/A')}" for field in fields)
#         formatted_properties.append(formatted_prop)
#     return '\n\n'.join(formatted_properties)


def fetch_images(properties, headers=headers):
    """
    Fetches up to 3 images for each property using the Zillow API or fallback to imgSrc.

    :param properties: list - A list of dictionaries representing properties, each with a 'zpid' or 'imgSrc'.
    :param headers: dict - HTTP headers for the API request.
    :return: list - The updated list of properties with image URLs included.
    """
    images_url = "https://zillow-com1.p.rapidapi.com/images"
    
    for prop in properties:
        try:
            # Attempt to use imgSrc if available
            if "imgSrc" in prop and prop["imgSrc"]:
                prop["images"] = [prop["imgSrc"]]
                continue
            
            # Use zpid if available
            zpid = prop.get("zpid")
            print(zpid)
            if not zpid:
                prop["images"] = ["No images available"]
                continue  # Skip if no zpid is available

            # Make the API call
            querystring = {"zpid":zpid}
            response = requests.get(images_url, headers=headers, params=querystring)
            
            # Handle potential rate-limiting (429)
            if response.status_code == 429:
                print(f"Rate-limited for property {prop.get('address', 'unknown')}. Retrying after a delay.")
                time.sleep(1)  # Exponential backoff can be added here
                response = requests.get(images_url, headers=headers, params=querystring)
            
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Extract up to 3 image URLs
            images = response.json().get("images", [])
            prop["images"] = images[:3] if images else ["No images available"]

        except Exception as e:
            print(f"Error fetching images for property {prop.get('address', 'unknown')}: {e}")
            prop["images"] = ["No images available"]  # Fallback in case of an error

    return properties



def fetch_top_properties_detail(api_filter, url=url, headers=headers):
    response = requests.get(url, headers = headers, params = api_filter)
    
    # get top 3 listings(sorted by newest)
    # Define fields to extract
    fields = ["propertyType", "address", "price", "bedrooms", "bathrooms", "detailUrl", "imgSrc", "longitude", "latitude"]
    top_properties = extract_properties(response, fields)
    
    # get description of the properties
    top_properties = fetch_descriptions(top_properties)

    # get resoFacts(detail) of the properties
    keys_to_fetch_resoFacts = [
        'hasGarage', 'hasPetsAllowed', 'heating', 'cooling', 'flooring', 'appliances',
        'laundryFeatures', 'associationFee',
        'livingArea', 'taxAnnualAmount', 'parkingFeatures', 'stories'
    ]
    top_properties = fetch_resoFacts(top_properties, keys_to_fetch_resoFacts)

    # get school info of the properties
    top_properties = fetch_schools(top_properties, headers)
    
    return top_properties