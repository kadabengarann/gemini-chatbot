import requests
import os
from flask import current_app
from app.utils.json_utils import (
    messages_to_dict,
    messages_from_dict,
)

API_URL = os.environ.get('API_URL')

def authenticate_user(identifier):
    url = API_URL + '/auth' + '?Identifier=identifier'
    
    response = requests.get(url)

    if response.status_code == 401:
        return False

    # Parse the response JSON
    response_data = response.json()

    # Check if the authentication was successful
    if not response_data.get('Result', {}).get('IsSuccess', False):
        return False

    conversation_history = messages_to_dict(response_data['ConversationHistory'])
    return conversation_history

def store_chat_history(chat_data, identifier):
    conversation_history = messages_from_dict(chat_data)
    url = API_URL + '/store_chat'
    payload = conversation_history
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 401:
        return False

    # Parse the response JSON
    response_data = response.json()

    # Check if the authentication was successful
    if not response_data.get('Result', {}).get('IsSuccess', False):
        return False

    return True

def retrieve_chat_history(user_id):
    url = f'https://external-api.com/chat/history/{user_id}'

    response = requests.get(url)
    return response.json()