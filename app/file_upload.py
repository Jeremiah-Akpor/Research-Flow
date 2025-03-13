import os
import json
import requests
import streamlit as st
import base64
# from docling.document_converter import DocumentConverter
import pymupdf4llm
from pathlib import Path
from app import app_utils
from app.history import ChatHistory
from app.dify import llm_chat
from app.app_settings import AppSettings

# Paths for file mappings and markdown storage
FILE_MAPPING_PATH = "app/uploads/file_mappings.json"
MARKDOWN_DIR = "app/uploads/converted_markdown"
IMAGE_DIR = "app/uploads/converted_images"

settings = AppSettings()


def load_file_mappings():
    """Load the mapping of files to their Dify IDs."""
    if os.path.exists(FILE_MAPPING_PATH):
        try:
            with open(FILE_MAPPING_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle empty or invalid JSON file
            st.warning(f"File {FILE_MAPPING_PATH} is empty or invalid. Resetting.")
            return {}
    return {}


def save_file_mappings(file_mappings):
    """Save the mapping of files to their Dify IDs."""
    with open(FILE_MAPPING_PATH, "w") as f:
        json.dump(file_mappings, f, indent=4)


def check_if_already_converted(file_name):
    """
    Check if the file has already been converted.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        tuple: (bool, str) indicating whether the file is converted and the path to the markdown file.
    """
    converted_file_path = os.path.join(MARKDOWN_DIR, f"{file_name}.md")
    return os.path.exists(converted_file_path), converted_file_path


def process_file_with_docling(file_path: str):
    """
    Process the file using Docling to extract structured content and images.

    Args:
        file_path (str): The path to the file.

    Returns:
        tuple: Markdown content and a list of saved image paths.
    """
    try:
        # converter = DocumentConverter()
        # result = converter.convert(file_path)
        markdown_content = pymupdf4llm.to_markdown(file_path)

        return markdown_content

    except AttributeError as e:
        raise RuntimeError(f"Attribute error during Docling conversion: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error during Docling conversion: {str(e)}")


def save_markdown(file_name, markdown_content):
    """
    Save the converted Markdown content to a file, removing .pdf extension.

    Args:
        file_name (str): The name of the file.
        markdown_content (str): The markdown content to save.

    Returns:
        str: The path to the saved markdown file.
    """
    os.makedirs(MARKDOWN_DIR, exist_ok=True)

    # Remove .pdf extension
    base_name = os.path.splitext(file_name)[0]

    # Save as .md file
    markdown_path = os.path.join(MARKDOWN_DIR, f"{base_name}.md")
    with open(markdown_path, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)

    return markdown_path, f"{base_name}.md"


def upload_to_dify(file_path: str, file_name: str):
    """
    Upload the processed file to Dify.

    Args:
        file_path (str): The path of the file being uploaded.
        markdown_content (str): The converted Markdown content.

    Returns:
        dict: The uploaded file metadata.
    """
    
    url = f"{settings.DIFY_API_URL}/files/upload"
    remote_api_key = settings.DIFY_API_KEY

    # print("file_path", file_path)
    # print("file_name", file_name)

    # Open the file in binary mode for upload
    with open(file_path, "rb") as file:
        files = {
            "file": (file_name, file, "text/markdown"),
        }
        data = {
            "user": "ResearchFlow",
            "type": "MD",
        }
        headers = {
            "Authorization": f"Bearer {remote_api_key}",
        }
        # Make the POST request
        response = requests.post(url, headers=headers, files=files, data=data)

    if response.ok:
        st.success("File uploaded to dify successfully")
        return response.json()
        
    else:
        st.error(
            f"Error uploading file: {response.status_code}, {response.text}"
        )





@st.dialog("Upload File 📎", width="large")
def upload_file( ):
    file_mappings = load_file_mappings()
    con = st.container()
    # Chat_session = settings.SELECTED_CHAT


    with con:
        file_types = [
            "pdf",
            # "docx",
            # "txt",
            # "csv",
            # "html",
            # "md",
            # "png",
            # "jpg",
            # "jpeg",
            # "gif",
            # "webp",
            # "svg",
        ]  # Added image formats

        # def file_uploaded( ):
        #     uploaded_file = st.session_state["file_uploader"]

        #     if uploaded_file is not None:
        #         save_dir = "app/uploads/uploaded_files"
        #         os.makedirs(save_dir, exist_ok=True)
        #         save_path = os.path.join(save_dir, uploaded_file.name)
        #         with con:
        #             with st.spinner(f"Uploading to Dify and Generating Report...", show_time=True):
        #                 st.write(f"Don't close")
        #                 try:
        #                     # Save the file locally
        #                     with open(save_path, "wb") as f:
        #                         f.write(uploaded_file.getbuffer())
                            
        #                     # Convert the file
        #                     markdown_content = process_file_with_docling(save_path)
        #                     markdown_path, file_name = save_markdown(
        #                         uploaded_file.name, markdown_content
        #                     )

        #                     # st.success(
        #                     #     f"File {file_name} successfully converted."
        #                     # )

        #                     # Upload the file to Dify
        #                     file_info = upload_to_dify(
        #                         markdown_path, file_name
        #                     )
        #                     chat_history = ChatHistory()
        #                     # print("File upload info:", file_info)
        #                     # file_mappings[uploaded_file.name] = file_info["id"]
        #                     new_chat = st.session_state["new_chat"]
        #                     dify_query = {
        #                             "Query": "Generate Paper Report",
        #                             "ResearchPaper": {
        #                             "transfer_method": "local_file",
        #                             "upload_file_id": file_info["id"],
        #                             "type": "document"
        #                             },
        #                             "Knownledge_Base_Name": file_name,
        #                             "new_chat": "False",
        #                         }
        #                     title, report= llm_chat( dify_query,  settings, [])

        #                     if new_chat:
        #                         if "file_info" not in st.session_state:
        #                             st.session_state["file_info"] = {"name" : file_name, "id" : file_info["id"], "report": report, "title" : title, "query": dify_query}
        #                         else:
        #                             st.session_state["file_info"] = {"name" : file_name, "id" : file_info["id"], "report": report, "title" : title, "query": dify_query}
                                
        #                         chat_history.create_chat_session(title)
        #                         if title is not None:
        #                             settings.SELECTED_CHAT = title
        #                             settings.save()
        #                         st.session_state["new_chat"] = False
        #                     # else:
        #                     #     st.session_state["file_info"] = {"name" : file_name, "id" : file_info["id"], "report": report, "title" : title, "query": dify_query}
                                
        #                     chat_history.save_file_info(Chat_session,file_name, file_info["id"])
        #                     # save_file_mappings(file_mappings)

        #                     dify_query["Query"] = f"Generate a report for : '{title}'"
        #                     temp_input = json.dumps(dify_query)

        #                     user_input_id = chat_history.add_user_input(settings.SELECTED_CHAT,  temp_input)
        #                     app_utils.print_ai_response(report,  settings.SELECTED_CHAT, chat_history, user_input_id)
        #                     chat_history.load_chat_into_session_state(settings.SELECTED_CHAT)

        #                     con.success(
        #                         f"File {file_name} processed, uploaded, and report generated successfully."
        #                     )

        #                     # Remove the uploaded file
        #                     uploaded_files_path = "app/uploads/uploaded_files"
        #                     files = os.listdir(uploaded_files_path)
        #                     for file in files:
        #                         os.remove(os.path.join(uploaded_files_path, file))
        #                         file_mappings.clear()
        #                         save_file_mappings(file_mappings)
        #                     converted_files = os.listdir(MARKDOWN_DIR)
        #                     for file in converted_files:
        #                         os.remove(os.path.join(MARKDOWN_DIR, file))
                            
                            
                            
        #                 except Exception as e:
        #                     con.error(f"Error: {str(e)}")

        # File uploader widget
        con.file_uploader(
            "Choose a file",
            label_visibility="collapsed",
            type=file_types,
            key="file_uploader",
            accept_multiple_files=False,
            #on_change=file_uploaded,
        )

        if con.file_uploader:
            uploaded_file = st.session_state["file_uploader"]

            if uploaded_file is not None:
                save_dir = "app/uploads/uploaded_files"
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, uploaded_file.name)
                with con:
                    with st.spinner(f"Uploading to Dify and Generating Report...", show_time=True):
                        st.write(f"Don't close the Dialog while processing")
                        try:
                            # Save the file locally
                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            
                            # Convert the file
                            markdown_content = process_file_with_docling(save_path)
                            markdown_path, file_name = save_markdown(
                                uploaded_file.name, markdown_content
                            )

                            # st.success(
                            #     f"File {file_name} successfully converted."
                            # )

                            # Upload the file to Dify
                            file_info = upload_to_dify(
                                markdown_path, file_name
                            )
                            chat_history = ChatHistory()
                            # print("File upload info:", file_info)
                            # file_mappings[uploaded_file.name] = file_info["id"]
                            new_chat = st.session_state["new_chat"]
                            dify_query = {
                                    "Query": "Generate Paper Report",
                                    "ResearchPaper": {
                                    "transfer_method": "local_file",
                                    "upload_file_id": file_info["id"],
                                    "type": "document"
                                    },
                                    "Knownledge_Base_Name": file_name,
                                    "new_chat": "False",
                                }
                            title, report= llm_chat( dify_query,  settings, [])

                            if new_chat:
                                st.session_state["file_info"] = {
                                    "name": file_name,
                                    "id": file_info["id"],
                                    "report": report,
                                    "title": title,
                                    "query": dify_query,
                                }
                                chat_history.create_chat_session(title)
                                if title:
                                    settings.SELECTED_CHAT = title
                                    settings.save()
                                st.session_state["new_chat"] = False

                            sessions = chat_history.fetch_chat_sessions()
                            if title and settings.SELECTED_CHAT != title and title not in sessions:
                                chat_history.change_chat_name(settings.SELECTED_CHAT, title)
                                settings.SELECTED_CHAT = title
                                settings.save()

                            chat_history.save_file_info(settings.SELECTED_CHAT,file_name, file_info["id"])
                            # save_file_mappings(file_mappings)

                            dify_query["Query"] = f"Generate a report for : '{title}'"
                            temp_input = json.dumps(dify_query)

                            user_input_id = chat_history.add_user_input(settings.SELECTED_CHAT,  temp_input)
                            app_utils.print_ai_response(report,  settings.SELECTED_CHAT, chat_history, user_input_id)
                            chat_history.load_chat_into_session_state(settings.SELECTED_CHAT)

                            con.success(
                                f"File {file_name} processed, uploaded, and report generated successfully."
                            )

                            # Remove the uploaded file
                            uploaded_files_path = "app/uploads/uploaded_files"
                            files = os.listdir(uploaded_files_path)
                            for file in files:
                                os.remove(os.path.join(uploaded_files_path, file))
                                file_mappings.clear()
                                save_file_mappings(file_mappings)
                            converted_files = os.listdir(MARKDOWN_DIR)
                            for file in converted_files:
                                os.remove(os.path.join(MARKDOWN_DIR, file))
                            
                            st.rerun()
                            
                        except Exception as e:
                            con.error(f"Error: {str(e)}")

        # # Manage uploaded files
        # uploaded_files_path = "app/uploads/uploaded_files"
        # if os.path.exists(uploaded_files_path):
        #     files = os.listdir(uploaded_files_path)
        #     if files:
        #         st.write("Files in upload directory:")
        #         selected_file = st.radio("Select a file to delete:", files)
        #         col, col2 = st.columns(2)
        #         if selected_file:
        #             file_path = os.path.join(uploaded_files_path, selected_file)
        #             if col.button(f"Delete {selected_file}"):
        #                 os.remove(file_path)
        #                 if selected_file in file_mappings:
        #                     del file_mappings[selected_file]
        #                     save_file_mappings(file_mappings)
        #                 st.success(f"{selected_file} deleted successfully")
        #         if col2.button("Delete All Files"):
        #             for file in files:
        #                 os.remove(os.path.join(uploaded_files_path, file))
        #             file_mappings.clear()
        #             save_file_mappings(file_mappings)
        #             st.success("All files deleted successfully")
        #     else:
        #         st.write("No files uploaded yet.")
        # else:
        #     st.write("Upload directory does not exist.")
