import warnings
from flask import current_app

warnings.filterwarnings("ignore", category=DeprecationWarning)
IS_USING_GPT = None
IS_USING_API = None
IS_USING_EXTERNAL_PROVIDER = None
EXTERNAL_PROVIDER_NAME = None

def generate_response(response, identifier, message_type=""):
    IS_USING_API = current_app.config['IS_USING_API']
    IS_USING_GPT = current_app.config['IS_USING_GPT']
    IS_USING_EXTERNAL_PROVIDER = current_app.config['IS_USING_EXTERNAL_PROVIDER']
    EXTERNAL_PROVIDER_NAME = current_app.config['EXTERNAL_PROVIDER_NAME']

    if IS_USING_API:
      if IS_USING_GPT:
        from ..services.gpt_service_api  import generate_response as model_generate_response
      elif IS_USING_EXTERNAL_PROVIDER:
        if EXTERNAL_PROVIDER_NAME == "Together":
          from .together_service_api  import generate_response as model_generate_response
        elif EXTERNAL_PROVIDER_NAME == "OpenRouter":
          from .open_router_service_api  import generate_response as model_generate_response
      else:
        from ..services.gemini_service_api  import generate_response as model_generate_response
    else:
      if IS_USING_GPT:
        from ..services.gpt_service  import generate_response as model_generate_response
      else:
        from ..services.gemini_service  import generate_response as model_generate_response
  
    return model_generate_response(response, identifier, message_type)