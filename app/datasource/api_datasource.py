import yaml
from flask import current_app
from langchain_community.tools.json.tool import JsonSpec
from langchain_community.utilities.requests import RequestsWrapper
from langchain_community.agent_toolkits import OpenAPIToolkit
from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from ..toolkit.custom_openapi_toolkit import CustomOpenAPIToolkit
import os
import pickle

# Function to construct API authentication headers
def construct_vms_api_auth_headers():
    access_token = current_app.config.get('VMS_API_KEY')
    return {"Authorization": f"Bearer {access_token}"}

def get_api_toolkit(model): 
    cache_file = "app/datasource/reduced_spec_cache.pkl"
    
    # Check if the reduced spec is cached
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            reduced_spec_dict = pickle.load(f)
    else:
        # Load the OpenAPI spec for the VMS API
        with open("app/datasource/api_vms.yaml") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        
        # Reduce the OpenAPI spec to include only necessary parts
        reduced_spec = reduce_openapi_spec(data)
        
        # Convert the reduced spec to a dictionary
        reduced_spec_dict = {
            "servers": reduced_spec.servers,
            "description": reduced_spec.description,
            "endpoints": reduced_spec.endpoints
        }
        
        # Cache the reduced spec
        with open(cache_file, "wb") as f:
            pickle.dump(reduced_spec_dict, f)
    
    # Create the JsonSpec object with the reduced spec dictionary
    api_json_spec = JsonSpec(dict_=reduced_spec_dict)
    
    # Construct the OpenAPI toolkit
    headers = construct_vms_api_auth_headers()
    vms_api_requests_wrapper = RequestsWrapper(headers=headers)

    return CustomOpenAPIToolkit.from_llm(
        llm=model, 
        json_spec=api_json_spec, 
        requests_wrapper=vms_api_requests_wrapper, 
        allow_dangerous_requests=True,
        verbose=True,
        max_iterations=50,
        handle_parsing_errors=True
    )