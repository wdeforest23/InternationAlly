import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


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
