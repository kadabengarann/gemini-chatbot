import urllib
import warnings
from pathlib import Path as p
from pprint import pprint

from langchain import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain



model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

warnings.filterwarnings("ignore")

data_folder = p.cwd() / "data"
p(data_folder).mkdir(parents=True, exist_ok=True)

# pdf_url = "https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf"
pdf_url = "https://ardhysatrio.tech/Resume-Ardhy-Satrio.c92cba5d.pdf"
pdf_file = str(p(data_folder, pdf_url.split("/")[-1]))

urllib.request.urlretrieve(pdf_url, pdf_file)

pdf_loader = PyPDFLoader(pdf_file)
pages = pdf_loader.load_and_split()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
context = "\n\n".join(str(p.page_content) for p in pages)
texts = text_splitter.split_text(context)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_index = Chroma.from_texts(texts, embeddings).as_retriever()


prompt_template = """Answer the question using the provided context.

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