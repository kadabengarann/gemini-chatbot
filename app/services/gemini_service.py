import warnings
from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from app.datasource import remote_datasource as datasource
# from app.datasource import local_datasource as datasource

warnings.filterwarnings("ignore")

model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)

context = str(datasource.data_context)
texts = text_splitter.split_text(context)

vector_index = Chroma.from_texts(texts, embeddings).as_retriever()

prompt_template = """You are a assistant for answering question. Answer the question using the context data and answer it in the style of a professional.

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