import requests
import json
from llm import get_chat_response
from prompt_creation import generate_prompt_local_advisor, generate_prompt_local_advisor_response
from property_info import extract_json_to_dict

def generate_local_search_query(chat, instruction, user_query):
    """
    Refines the user's query for Local Advisor using LLM.

    Args:
        chat (object): The chat instance for interacting with the LLM.
        instruction (str): Instruction template for the LLM.
        user_query (str): The user's query to refine.

    Returns:
        dict: A JSON object with "search_string" and "included_type" fields.
    """
    # Generate the prompt
    prompt = generate_prompt_local_advisor(instruction, user_query)

    # Get the response from the LLM
    response = get_chat_response(chat, prompt)

    # Extract and parse the JSON from the response
    refined_query = extract_json_to_dict(response)
    if isinstance(refined_query, str):  # If it's an error message
        raise ValueError(f"Invalid JSON response from LLM: {response}")

    return refined_query


def search_google_places(api_key, search_string, included_type):
    """
    Performs a Google Places Text Search (New) based on the provided parameters.

    Args:
        api_key (str): Your Google Maps API key.
        search_string (str): The search query for the Places API (e.g., "pizza in New York").
        included_type (str): The most relevant type for the search (e.g., "restaurant").

    Returns:
        list: A list of results (place details) from the Google Places API.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    # Default location bias set to Chicago coordinates
    location_bias = {"lat": 41.8781, "lng": -87.6298}

    # Construct the parameters
    params = {
        "query": search_string,
        "key": api_key,
        "type": included_type,
        "region": "us",
        "language": "en-US",
        "locationbias": f"point:{location_bias['lat']},{location_bias['lng']}",
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Handle the response
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            return data["results"]
        else:
            print("No results found.")
            return []
    else:
        raise ValueError(f"Google Places API error: {response.status_code} {response.text}")

def generate_local_advisor_response(chat, instruction, user_query, places):
    """
    Generates a response for the Local Advisor using LLM.

    Args:
        chat (object): The chat instance for interacting with the LLM.
        instruction (str): Instruction template for the LLM.
        user_query (str): The user's query.
        places (list): A list of places from the Google Places API.

    Returns:
        str: The generated response from the LLM.
    """
    # Prepare the input for the LLM
    prompt = generate_prompt_local_advisor_response(instruction, user_query, places)

    # Get the response from the LLM
    response = get_chat_response(chat, prompt)
    return response