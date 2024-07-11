import logging
import json
import time
from threading import Thread

from flask import Blueprint, request, jsonify, current_app
from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)
from .services.model_service  import generate_response

webhook_blueprint = Blueprint("webhook", __name__)

def is_timestamp_within_1_minutes(timestamp):
    current_time = int(time.time())
    limin_minutes = current_time - 60  # 120 seconds = 2 minutes
    return timestamp > limin_minutes

def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    app_context = current_app.app_context()
    
    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            logging.info(f"Processing message: {body}")
            try:
                message_timestamp = int(body["entry"][0]["changes"][0]["value"]["messages"][0]["timestamp"])
                if is_timestamp_within_1_minutes(message_timestamp) is False:
                    logging.info("------------------------------------------------------------------------------------Message is too old------------------------------------------------------------------------------------")
                    return jsonify({"status": "ok"}), 200
                # Process the message in a new thread
                thread = Thread(target=process_whatsapp_message, args=(body,app_context))
                thread.start()
            except Exception as e:
                logging.error(f"Error processing WhatsApp message: {e}")
                return (
                    jsonify({"status": "error", "message": "Failed to process WhatsApp message"}),
                    500,
                )
            logging.info("Response status: OK 200")
            return jsonify({"status": "ok"}), 200
        else:
            # if the request is not a WhatsApp API event, return an error
            logging.warning("Received a non-WhatsApp API event.")
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400


# Required webhook verifictaion for WhatsApp
def verify():
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            # Respond with 200 OK and challenge token from the request
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()


# New routes
@webhook_blueprint.route('/', methods=['GET'])
def hello():
    return jsonify({"IsSuccess": True})
    
@webhook_blueprint.route('/start', methods=['GET'])
def start_conversation():
    print("Starting a new conversation...")
    return jsonify({"chat_id": 123213123})

@webhook_blueprint.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    user_code = data.get('code', '')

    assistant_response = generate_response(user_input, user_code)
    if not assistant_response:
        assistant_response = "Sorry, you are not authorized to use this service."

    print(f"Assistant response: {assistant_response}")  # Debugging line
    return jsonify({"response": assistant_response})

@webhook_blueprint.route('/testing', methods=['GET'])
def testing():
    user_input = "give me one of the user's name"

    assistant_response = generate_response(user_input, "slec4789")

    print(f"Assistant response: {assistant_response}")  # Debugging line
    return jsonify({"response": assistant_response,
                    "model-name": current_app.config['MODEL_NAME']
                   })