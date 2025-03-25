import os
import torch
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from dotenv import load_dotenv
import warnings

warnings.filterwarnings("ignore")
load_dotenv()

def retrieve_response(user_input: str) -> str:

    """
    Gets an user input and returns a response which answers what was asked in the input.

    Parameters:
    - user_input (str) : the user query to be added to a prompt to be sent to the model

    Returned value:
    - str : model's response from the given prompt
    """

    # Load FAISS and retrieve relevant documents based on a query
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("data/faiss_index", embeddings, allow_dangerous_deserialization=True)

    query = user_input
    retrieved_docs = vectorstore.similarity_search(query, k=3)

    for doc in retrieved_docs:
        print(doc.page_content)

    # Load a quantized CPU-compatible LLM model
    model_name = "Qwen/Qwen2.5-1.5B"

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=os.getenv("HUGGINGFACE_INFERENCE_TOKEN"))

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",         # Force CPU usage
        torch_dtype=torch.float16, # Reduce memory usage
        use_auth_token=os.getenv("HUGGINGFACE_INFERENCE_TOKEN")
    )

    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)  # Ensure CPU execution

    # Combine retrieved chunks for context
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    prompt = f"Answer the following question based on the context:\n\nContext:\n{context}\n\nQuestion: {query}"

    response = generator(prompt, max_length=400)[0]["generated_text"]
    return response.split(prompt)[1]

if __name__ == "__main__":

    user_input = "What is the command used to create a branch?"#"What is the main topic of the documents?"

    response = retrieve_response(user_input)
    print(f"Response: {response.strip()}")
