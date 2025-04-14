import warnings
import logging
from datetime import datetime
from flask import current_app
from ..services import external_api_service as api_service, prompt
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.agent_toolkits import create_openapi_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ChatMessageHistory

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global variables
_model = None
_toolkit = None
agent = None
stuff_chain = None
vector_index = None
IS_USING_DB = None
IS_USING_API = None
DATA_API_URL = None
_datasource = None

def get_datasource():
    """Return the appropriate datasource based on the current configuration."""
    global _datasource, IS_USING_API
    if _datasource is None:
        IS_USING_API = current_app.config['IS_USING_API']
        from app.datasource import api_datasource as datasource
        _datasource = datasource
    return _datasource

def initialize_model():
    """Initialize and return the ChatOpenAI model."""
    global _model
    if _model is None:
        model_name = current_app.config.get('MODEL_NAME')
        if not model_name:
            raise ValueError("MODEL_NAME environment variable not set")
        _model = ChatOpenAI(model_name=model_name, temperature=0.3)
    return _model

def initialize_api_agent(model, openapi_toolkit, conversational_memory, user_name): 
    """Initialize and return the API agent."""

    global DATA_API_URL
    if DATA_API_URL is None:
        DATA_API_URL = current_app.config.get('DATA_API_URL')
        if not DATA_API_URL:
            raise ValueError("API_URL environment variable not set")
    raw_prefix_template = prompt.OPENAPI_PREFIX
    return create_openapi_agent(
        llm=model,
        toolkit=openapi_toolkit,
        prefix=raw_prefix_template.format(api_base_url=DATA_API_URL),
        suffix=prompt.OPENAPI_SUFFIX,
        format_instructions=prompt.FORMAT_INSTRUCTIONS,
        allow_dangerous_requests=True,
        input_variables=["input", "agent_scratchpad", "history", "user_name", "current_date", "current_day"],
        agent_executor_kwargs={
            'memory': conversational_memory,
            'handle_parsing_errors': True
        },
        handle_parsing_errors=True,
        verbose=True,
        early_stopping_method="generate"
    )

def initialize_stuff_chain(model):
    """Initialize and return the 'stuff' chain for non-DB cases."""
    prompts = PromptTemplate(template=prompt.ALL_PROMPT, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompts)

def authenticate_user(identifier, message_type):
    """Authenticate the user based on the identifier."""
    result = api_service.authenticate_user(identifier, message_type)
    return result if result else False

def store_chat_history(chat_data, identifier, message_type):
    """Store chat history for the user."""
    return api_service.store_chat_history(chat_data, identifier, message_type)

def generate_response(response, identifier, message_type=""):
    """Generate a response based on the user input and identifier."""
    logging.info(f"------- Processing Question From {message_type}")

    # Get the current date and day
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")

    
    authentication_result = authenticate_user(identifier, message_type)
    
    if authentication_result is False:
        logging.info(f"        Unauthorized User : {identifier} {authentication_result}")
        return False
        
    logging.info(f"        Authorized User : {identifier}")
    username, extracted_messages = authentication_result
    global agent, _toolkit
    
    datasource = get_datasource()
    model = initialize_model()
    
    if _toolkit is None:
        _toolkit = datasource.get_api_toolkit(model, identifier)
    if _toolkit is None:
        return "api_toolkit not initialized"
        
    api_toolkit = _toolkit
    
    conversational_memory = ConversationSummaryBufferMemory(
        chat_memory=ChatMessageHistory(messages=extracted_messages),
        llm=model,
        max_token_limit=50,
        input_key='input'
    )

    if agent is None:
        agent = initialize_api_agent(model, api_toolkit, conversational_memory, username)
    if agent is None:
        return "Agent not initialized"
    input_dict = {
        "input": response,
        "user_name": username,
        "current_date": current_date,
        "current_day": current_day
    }

    assistant_response = agent.run(input_dict)
    # try:
    #     assistant_response = agent.run(input_dict)
    # except Exception as e:
    #     logging.error(f"Error during agent execution: {e}")
    #     return str(e)

    store_chat_history(agent.memory.chat_memory.messages, identifier, message_type)

    if "does not mention" in assistant_response:
        assistant_response = "Answer not available in context"

    logging.info("Assistant response: %s", assistant_response) # Debugging line
    return str(assistant_response)