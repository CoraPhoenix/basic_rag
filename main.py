import gradio as gr
from datetime import datetime
from pathlib import Path
import shutil
from rag.generate_response import retrieve_response
from rag.vectorbase_generator import generate_vectorstore
from meta.load_data import *
import logging

history = []

def update_database() -> None:

    """
    Updates vector database if any change on the source folder was detected.

    Parameters:
    None

    Returned value:
    None
    """

    try:
        logging.info("Checking if database is up to date...")
        current_meta = get_doc_metadata()
        update_meta = update_metadata()

        if update_meta:
            logging.info("Updating vector database...")
            generate_vectorstore()

    except Exception as e:
        logging.error(f" An error was detected: {str(e)}")
        raise SystemExit(str(e))

def add_file_to_source(file) -> None:
    """
    Uploads a file to the source folder.

    Parameters:
    file - file to be uploaded.

    Returned value:
    None
    """
    name = Path(file).name
    if name.endswith(".txt") or name.endswith(".pdf"):
        shutil.copy(file, "docs/")
        update_database()
        gr.Info("File uploaded successfully.")
    else:
        gr.Error("File must be a text (.txt) or PDF (.pdf) document.")

def get_info_from_input(user_input : str) -> list[str]:

    """
    Gets bot answer from input and saves it to a temporary history.

    Parameters:
    - user_input (str) : the user input to be answered

    Returned value:
    - list[str] : a list containing both answer and history
    """

    answer = retrieve_response(user_input)

    history.append(f"""
        Question: {input}
        Answer: {answer.strip()}
        Executed time: {datetime.now()}
        \n
    """)

    return answer, "\n".join(history[::-1])

def launch_app() -> None:

    """
    Gradio app function.

    Parameters:
    None

    Returned value:
    None
    """

    logging.info("Launching app...")

    with gr.Blocks() as demo:

        gr.Markdown(
            """
            # Simple RAG

            Welcome to the Simple RAG project!
            """
        )

        with gr.Tabs():

            with gr.TabItem("Ask the bot"):

                gr.Markdown("""Type in any question and, based on the database, the bot will readily answer you.
                Give it a try!""")

                with gr.Row():
                    with gr.Column():
                        # input fields
                        input_txt = gr.Textbox(label="Ask here")
                        question_button = gr.Button("Send")
                    with gr.Column():
                        # history and output fields
                        answer = gr.Textbox(label="Answer")
                        history_text = gr.Textbox(label="History", max_lines=15)
            
            with gr.TabItem("Upload documents"):

                gr.Markdown("This section is used to upload a file. Please click on the button below and add a .txt or .pdf file to the base.")

                upload_button = gr.UploadButton("Upload document (PDF or TXT)")
                
        question_button.click(fn=get_info_from_input, inputs=input_txt, outputs=[answer, history_text])
        upload_button.upload(add_file_to_source, upload_button)

    demo.launch()

if __name__ == "__main__":

    try:
        update_database()
        launch_app()
    except Exception as e:
        print(str(e))

