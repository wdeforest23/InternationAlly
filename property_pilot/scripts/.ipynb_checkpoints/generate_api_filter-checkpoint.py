# Importing required libraries
import pandas as pd
import numpy as np
import warnings
import json
warnings.filterwarnings('ignore')


def generate_prompt_apifilter(instruction, user_query):
    return instruction.replace("{USER_QUERY}", user_query)

def extract_json_to_dict(text):
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


