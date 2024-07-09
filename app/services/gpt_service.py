import warnings
import os
from ..services import external_api_service as api_service, prompt
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain_openai import ChatOpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentType, create_sql_agent
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory import ChatMessageHistory

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
load_dotenv()
IS_USING_DB = os.environ.get('IS_USING_DB')
if IS_USING_DB == 'False':
    IS_USING_DB = False
else:
    IS_USING_DB = True

print(f'Is Using SB {type(IS_USING_DB)} {IS_USING_DB}')

if IS_USING_DB:
    # Import modules or execute code for when IS_USING_DB is True
    from app.datasource import db_datasource as datasource
else:
    from app.datasource import remote_datasource as datasource

model_name = os.environ.get('MODEL_NAME')
agent = None
stuff_chain = None

# Initialization
model = ChatOpenAI(model_name=model_name, temperature=0.3)
if not IS_USING_DB:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
    context = str(datasource.data_context)
    texts = text_splitter.split_text(context)
    # vector_index = Chroma.from_texts(texts, embeddings).as_retriever()

#Promt for SQL based
template = "\n\n".join(
    [
        prompt.PREFIX, 
        "{tools}",
        prompt.FORMAT_INSTRUCTIONS,
        prompt.SUFFIX,
    ]
)

if IS_USING_DB:
    prompt = PromptTemplate.from_template(template)
    agent = create_sql_agent(llm=model, toolkit=datasource.get_toolkit(model), agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, prompt=prompt, verbose=True, handle_parsing_errors=True, early_stopping_method="force", max_iterations=12)
else:
    prompts = PromptTemplate(
        template=prompt.ALL_PROMPT, input_variables=["context", "question"]
    )
    stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompts)


# Functions
def authenticate_user(identifier):
    result = api_service.authenticate_user(identifier)
    if result is False:
        return False
    return result
def store_chat_history(chat_data, identifier):
    result = api_service.store_chat_history(chat_data, identifier)
    return result

def generate_response(response, identifier):
    print("---------------User Identifier :" + identifier)
    is_authenticated_result = authenticate_user(identifier)
    if is_authenticated_result is None:
        return False

    agent = None

    extracted_messages = is_authenticated_result
    # conversational_memory = ConversationEntityMemory(chat_memory=ChatMessageHistory(messages=extracted_messages),llm=model
    #     ,memory_key='history',k=2)
    conversational_memory = ConversationSummaryBufferMemory(chat_memory=ChatMessageHistory(messages=extracted_messages),llm=model
        , max_token_limit=50)

    global prompt
    if IS_USING_DB:
        agent = create_sql_agent(llm=model, 
             toolkit=datasource.get_toolkit(model), 
             agent_type="openai-tools",
             prompt=prompt, 
             input_variables=["input", "agent_scratchpad", "history"],
             agent_executor_kwargs={'memory': conversational_memory},
             verbose=True)

    global stuff_chain
    if agent is None and IS_USING_DB:
        return "Agent not initialized"
    if stuff_chain is None and not IS_USING_DB:
        return "Stuff chain not initialized"

    if IS_USING_DB:
        answer = agent.run(response)
        assistant_response = answer
        store_chat_history(agent.memory.chat_memory.messages, identifier)
    else:
        docs = vector_index.get_relevant_documents(response)
        stuff_answer = stuff_chain({"input_documents": docs, "question": response}, return_only_outputs=False)
        assistant_response = stuff_answer['output_text']

    if "does not mention" in assistant_response:
        assistant_response = "Answer not available in context"

    print(f"Assistant response: {assistant_response}")  # Debugging line
    return assistant_response