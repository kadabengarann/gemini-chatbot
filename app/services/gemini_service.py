import warnings
import os
import app.services.prompt as prompt
from dotenv import load_dotenv
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.agents import AgentType, create_sql_agent

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
model = ChatGoogleGenerativeAI(model=model_name, temperature=0.3)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
if not IS_USING_DB:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
    context = str(datasource.data_context)
    texts = text_splitter.split_text(context)
    vector_index = Chroma.from_texts(texts, embeddings).as_retriever()

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
    agent = create_sql_agent(llm=model, toolkit=db_datasource.get_toolkit(model),    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, prompt=prompt, verbose=True)
else:
    prompts = PromptTemplate(
        template=prompt.ALL_PROMPT, input_variables=["context", "question"]
    )
    stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompts)


# Functions
def generate_response(response):
    global agent
    global stuff_chain
    if agent is None and IS_USING_DB:
        return "Agent not initialized"
    if stuff_chain is None and not IS_USING_DB:
        return "Stuff chain not initialized"
    
    if IS_USING_DB:
        answer = agent.run(response)
        assistant_response = answer
    else:
        docs = vector_index.get_relevant_documents(response)
        stuff_answer = stuff_chain({"input_documents": docs, "question": response}, return_only_outputs=False)
        assistant_response = stuff_answer['output_text']

    if "does not mention" in assistant_response:
        assistant_response = "Answer not available in context"

    print(f"Assistant response: {assistant_response}")  # Debugging line
    return assistant_response
    
def generate_response_old(response):
    docs = vector_index.get_relevant_documents(response)

    stuff_answer = stuff_chain(
        {"input_documents": docs, "question": response}, return_only_outputs=False
    )
    assistant_response = stuff_answer['output_text']
    if "does not mention" in assistant_response:
        assistant_response = "answer not available in context"

    # print(f"Raw stuff_chain response: {stuff_answer}")  # Debugging line
    print(f"Assistant response: {assistant_response}")  # Debugging line

    return assistant_response

# Construct the prompt


def generate_response_uwaw(response):
    global agent
    if agent is None:
        return "Agent not initialized"

    if IS_USING_DB:
        answer = agent.run(response)
        assistant_response = answer
    else:
        docs = vector_index.get_relevant_documents(response)

        stuff_answer = stuff_chain(
            {"input_documents": docs, "question": response}, return_only_outputs=False
        )
        assistant_response = stuff_answer['output_text']
    if "does not mention" in assistant_response:
        assistant_response = "answer not available in context"

    # print(f"Raw stuff_chain response: {stuff_answer}")  # Debugging line
    print(f"Assistant response: {assistant_response}")  # Debugging line

    return assistant_response