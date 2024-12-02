import warnings
from flask import current_app

warnings.filterwarnings("ignore", category=DeprecationWarning)
IS_USING_GPT = None
IS_USING_API = None

def generate_response(response, identifier, message_type=""):
    IS_USING_API = current_app.config['IS_USING_API']
    IS_USING_GPT = current_app.config['IS_USING_GPT']

    if IS_USING_API:
      if IS_USING_GPT:
        from ..services.gpt_service_api  import generate_response as model_generate_response
      else:
        from ..services.gemini_service_api  import generate_response as model_generate_response
    else:
      if IS_USING_GPT:
        from ..services.gpt_service  import generate_response as model_generate_response
      else:
        from ..services.gemini_service  import generate_response as model_generate_response
  
    return model_generate_response(response, identifier, message_type)