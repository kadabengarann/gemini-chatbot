import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.environ['ACCESS_TOKEN']
    app.config["YOUR_PHONE_NUMBER"] = os.environ['YOUR_PHONE_NUMBER']
    app.config["APP_ID"] = os.environ['APP_ID']
    app.config["APP_SECRET"] = os.environ['APP_SECRET']
    app.config["RECIPIENT_WAID"] = os.environ['RECIPIENT_WAID']
    app.config["VERSION"] = os.environ['VERSION']
    app.config["PHONE_NUMBER_ID"] = os.environ['PHONE_NUMBER_ID']
    app.config["VERIFY_TOKEN"] = os.environ['VERIFY_TOKEN']


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
