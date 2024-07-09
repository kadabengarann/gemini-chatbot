import requests
import os
from flask import current_app
from ..utils.json_utils import messages_to_dict, messages_from_dict

# Define a function to get API URL from app context
def get_api_url():
    """
    Retrieves the API_URL from the current Flask application context.
    """
    with current_app.app_context():
        return current_app.config.get('API_URL')

# Initialize API_URL using the function above
#API_URL = "https://outdev.werkdone.com/VMS_BL/rest/ChatBot"

API_URL = ""

def handle_api_response(response):
    """
    Helper function to handle common error conditions in API responses.
    Returns parsed JSON data if successful, otherwise returns False.
    """
    global API_URL
    API_URL = get_api_url()
    if response.status_code == 401:
        return None

    try:
        response_data = response.json()
    except ValueError:
        return None

    if not response_data.get('Result', {}).get('IsSuccess', False):
        return None

    return response_data

def authenticate_user(identifier):
    global API_URL
    API_URL = get_api_url()
    """
    Authenticates the user based on the provided identifier.
    Returns conversation history as a list of dicts if authentication is successful, otherwise returns False.
    """
    url = f'{API_URL}/auth?Identifier={identifier}'
    response = requests.get(url)

    response_data = handle_api_response(response)
    if response_data is None:
        conversation_history = messages_to_dict([])
        return conversation_history

    conversation_history = messages_to_dict(response_data.get('ConversationHistory', []))
    return conversation_history

def store_chat_history(chat_data, identifier):
    global API_URL
    API_URL = get_api_url()
    """
    Stores chat history for the user identified by `identifier`.
    Returns True if storing was successful, otherwise returns False.
    """
    conversation_history = messages_from_dict(chat_data)
    url = f'{API_URL}/store_chat'
    payload = {
        "Identifier": identifier,
        "ChatbotLogList": conversation_history
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)

    response_data = handle_api_response(response)
    if response_data is None:
        return True

    return True

def retrieve_chat_history(user_id):
    url = f'https://external-api.com/chat/history/{user_id}'

    response = requests.get(url)
    return response.json()