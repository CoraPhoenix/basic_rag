import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import warnings

warnings.filterwarnings("ignore")

def load_documents(folder_path : str) -> list:

    """
    Load document files from a folder.

    Parameters:
    - folder_path (str): The document source folder path.

    Returned value:
    - list: a list containing extracted text from documents
    """

    documents = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            continue
        documents.extend(loader.load())
    return documents

def generate_vectorstore() -> HuggingFaceEmbeddings:

    """
    Creates a vector database from a set of documents.

    Parameters:
    None

    Returned value:
    - HuggingFaceEmbeddings: a HuggingFace embeddings object
    """

    docs = load_documents("docs/")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)

    # Load a CPU-friendly embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Convert document chunks into embeddings and store them in FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("data/faiss_index")

    return embeddings

if __name__ == "__main__":

    embeddings = generate_vectorstore()

