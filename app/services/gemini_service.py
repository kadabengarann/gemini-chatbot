import warnings
from datetime import datetime
from flask import current_app
from ..services import external_api_service as api_service, prompt
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.agents import AgentType, create_sql_agent
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ChatMessageHistory

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global variables
_model = None
_datasource = None
agent = None
stuff_chain = None
vector_index = None
IS_USING_DB = None

def get_datasource():
    """Return the appropriate datasource based on the current configuration."""
    global _datasource, IS_USING_DB
    if _datasource is None:
        IS_USING_DB = current_app.config['IS_USING_DB']
        if IS_USING_DB:
            from app.datasource import db_datasource as datasource
        else:
            from app.datasource import remote_datasource as datasource
        _datasource = datasource
    return _datasource

def initialize_model():
    """Initialize and return the ChatOpenAI model."""
    global _model
    if _model is None:
        model_name = current_app.config.get('MODEL_NAME')
        if not model_name:
            raise ValueError("MODEL_NAME environment variable not set")
        _model = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
    return _model

def initialize_sql_agent(model, datasource, conversational_memory, user_name): 
    """Initialize and return the SQL agent."""
    # Get the current date and day
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")

    template = "\n\n".join([prompt.PREFIX, "{tools}", prompt.FORMAT_INSTRUCTIONS, prompt.SUFFIX])
    sql_prompt = PromptTemplate.from_template(
        template,
        input_variables=["input", "agent_scratchpad", "history", "user_name", "current_date", "current_day"]
    )
    return create_sql_agent(
        llm=model,
        toolkit=datasource.get_toolkit(model),
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prompt=sql_prompt,
        input_variables=["input", "agent_scratchpad", "history", "user_name", "current_date", "current_day"],
        agent_executor_kwargs={'memory': conversational_memory},
        handle_parsing_errors=True,
        verbose=True
    )

def initialize_stuff_chain(model):
    """Initialize and return the 'stuff' chain for non-DB cases."""
    prompts = PromptTemplate(template=prompt.ALL_PROMPT, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompts)

def authenticate_user(identifier):
    """Authenticate the user based on the identifier."""
    result = api_service.authenticate_user(identifier)
    return result if result else False

def store_chat_history(chat_data, identifier):
    """Store chat history for the user."""
    return api_service.store_chat_history(chat_data, identifier)

def generate_response(response, identifier):
    """Generate a response based on the user input and identifier."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    print(f"---------------User Identifier : {identifier}")
    authentication_result = authenticate_user(identifier)
    if authentication_result is False:
        print(f"---------------Unauthorized User : {identifier} {authentication_result}")
        return False
    print(f"---------------Authorized User : {identifier}")
    username, extracted_messages = authentication_result
    global agent, stuff_chain, vector_index

    datasource = get_datasource()
    model = initialize_model()

    # conversational_memory = ConversationEntityMemory(chat_memory=ChatMessageHistory(messages=extracted_messages),llm=model
    #     ,memory_key='history',k=2)
    conversational_memory = ConversationSummaryBufferMemory(
        chat_memory=ChatMessageHistory(messages=extracted_messages),
        llm=model,
        max_token_limit=50
    )

    if IS_USING_DB:
        if agent is None:
            agent = initialize_sql_agent(model, datasource, conversational_memory, username)
        if agent is None:
            return "Agent not initialized"
        assistant_response = agent.run(response)
        store_chat_history(agent.memory.chat_memory.messages, identifier)
    else:
        if stuff_chain is None:
            stuff_chain = initialize_stuff_chain(model)
        if stuff_chain is None:
            return "Stuff chain not initialized"
        if vector_index is None:
            context = str(datasource.data_context)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
            texts = text_splitter.split_text(context)
            # Initialize the vector index (assuming `embeddings` is defined and properly set up)
            vector_index = Chroma.from_texts(texts, embeddings).as_retriever()
        docs = vector_index.get_relevant_documents(response)
        stuff_answer = stuff_chain({"input_documents": docs, "question": response}, return_only_outputs=False)
        assistant_response = stuff_answer['output_text']

    if "does not mention" in assistant_response:
        assistant_response = "Answer not available in context"

    print(f"Assistant response: {assistant_response}")  # Debugging line
    return assistant_response