import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv('ACCESS_TOKEN', os.environ.get('ACCESS_TOKEN'))
    app.config["APP_ID"] = os.getenv('APP_ID', os.environ.get('APP_ID'))
    app.config["APP_SECRET"] = os.getenv('APP_SECRET', os.environ.get('APP_SECRET'))
    app.config["VERSION"] = os.getenv('VERSION', os.environ.get('VERSION'))
    app.config["PHONE_NUMBER_ID"] = os.getenv('PHONE_NUMBER_ID', os.environ.get('PHONE_NUMBER_ID'))
    app.config["VERIFY_TOKEN"] = os.getenv('VERIFY_TOKEN', os.environ.get('VERIFY_TOKEN'))
    app.config["MODEL_NAME"] = os.getenv('MODEL_NAME', os.environ.get('MODEL_NAME'))
    app.config["DB_URI"] = os.getenv('DB_URI', os.environ.get('DB_URI'))
    app.config["IS_USING_DB"] = os.environ.get('IS_USING_DB')
    if app.config["IS_USING_DB"] == "False":
        app.config["IS_USING_DB"] = False
    else:
        app.config["IS_USING_DB"] = True
    app.config["API_URL"] = os.getenv('API_URL', os.environ.get('API_URL'))
    os.environ['LANGCHAIN_TRACING_V2']="true"
    os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
    os.environ['LANGCHAIN_API_KEY']= os.getenv('LANGCHAIN_API_KEY', os.environ.get('LANGCHAIN_API_KEY', ''))
    os.environ['LANGCHAIN_PROJECT']="wd-chatbot"


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
