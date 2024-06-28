import requests
import os
from flask import current_app
from app.utils.json_utils import (
    messages_to_dict,
    messages_from_dict,
)

API_URL =  os.environ.get('API_URL')

def handle_api_response(response):
    """
    Helper function to handle common error conditions in API responses.
    Returns parsed JSON data if successful, otherwise returns False.
    """
    if response.status_code == 401:
        return False

    try:
        response_data = response.json()
    except ValueError:
        return False

    if not response_data.get('Result', {}).get('IsSuccess', False):
        return False

    return response_data

def authenticate_user(identifier):
    """
    Authenticates the user based on the provided identifier.
    Returns conversation history as a list of dicts if authentication is successful, otherwise returns False.
    """
    url = f'{API_URL}/auth?Identifier={identifier}'
    response = requests.get(url)

    response_data = handle_api_response(response)
    if not response_data:
        return False

    conversation_history = messages_to_dict(response_data.get('ConversationHistory', []))
    return conversation_history

def store_chat_history(chat_data, identifier):
    """
    Stores chat history for the user identified by `identifier`.
    Returns True if storing was successful, otherwise returns False.
    """
    conversation_history = messages_from_dict(chat_data)
    url = f'{API_URL}/store_chat'
    payload = conversation_history
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)

    response_data = handle_api_response(response)
    if not response_data:
        return False

    return True

def retrieve_chat_history(user_id):
    url = f'https://external-api.com/chat/history/{user_id}'

    response = requests.get(url)
    return response.json()