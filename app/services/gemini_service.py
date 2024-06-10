import warnings
from flask import current_app
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from app.datasource import remote_datasource as datasource
# from app.datasource import local_datasource as datasource

warnings.filterwarnings("ignore")
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3) #gemini-1.5-pro
# model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3) #gemini-1.5-pro
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)

context = str(datasource.data_context)
texts = text_splitter.split_text(context)

vector_index = Chroma.from_texts(texts, embeddings).as_retriever()

prompt_template = """You are a assistant for a system to answering users question. Answer the question using the context data and answer it in professional way. If answer include a date format it should be in the format including day of the week that easily undestandable.

Context: 
{context}

Question: 
{question}

Answer:
"""

prompts = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompts)

def generate_response(response):
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
