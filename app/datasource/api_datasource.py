import yaml
from flask import current_app
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities.requests import RequestsWrapper
from langchain_community.agent_toolkits import OpenAPIToolkit

# Load the OpenAPI spec for the VMS API
with open("api_vms.yaml") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
api_json_spec = JsonSpec(dict_=data)

# Function to construct API authentication headers
def construct_vms_api_auth_headers():
    access_token = current_app.config.get('VMS_API_KEY')
    return {"Authorization": f"Bearer {access_token}"}

def get_api_toolkit(model, json_spec): 
    headers = construct_vms_api_auth_headers()
    vms_api_requests_wrapper = RequestsWrapper(headers=headers)

    return OpenAPIToolkit.from_llm(
        llm=model, 
        json_spec = json_spec, 
        requests_wrapper = vms_api_requests_wrapper, 
        allow_dangerous_requests= True,
        verbose=True
    )