import warnings
from flask import current_app

warnings.filterwarnings("ignore", category=DeprecationWarning)
IS_USING_GPT = None

def generate_response(response, identifier):
    IS_USING_GPT = current_app.config['IS_USING_GPT']

    if IS_USING_GPT:
      from ..services.gpt_service  import generate_response as model_generate_response
    else:
      from ..services.gemini_service  import generate_response as model_generate_response
  
    return model_generate_response(response, identifier)