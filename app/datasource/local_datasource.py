import warnings
import urllib
import os
from pathlib import Path as p
from langchain.document_loaders import PyPDFLoader

warnings.filterwarnings("ignore")

data_folder = p.cwd() / "data"
p(data_folder).mkdir(parents=True, exist_ok=True)

'''
# pdf_url = "https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf"
pdf_url = "https://ardhysatrio.tech/Resume-Ardhy-Satrio.c92cba5d.pdf"
pdf_file = str(p(data_folder, pdf_url.split("/")[-1]))

urllib.request.urlretrieve(pdf_url, pdf_file)

pdf_loader = PyPDFLoader(pdf_file)
'''

# if local, use this
# Specify the path to your local PDF file in the same directory
pdf_filename = "data/Jprint.pdf"  # Replace with your actual PDF file name

# Create the full path to the PDF file
pdf_file = os.path.join(os.getcwd(), pdf_filename)

# Check if the file exists before proceeding
if not os.path.isfile(pdf_file):
    raise ValueError(f"File path {pdf_file} is not a valid file")

pdf_loader = PyPDFLoader(pdf_file)

pages = pdf_loader.load_and_split()

data_context = "\n\n".join(str(p.page_content) for p in pages)