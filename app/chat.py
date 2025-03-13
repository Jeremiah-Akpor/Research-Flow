import streamlit as st  # Import Streamlit for web app creation
import logging  # Import logging for logging purposes
import os  # Import time for delay simulation
from streamlit.delta_generator_singletons import get_dg_singleton_instance
from app.file_upload import upload_file
import app.state_manager as state_manager  # Import state_manager for state management
import app.app_utils as app_utils
import app.markdown as markdown
from app.dify import llm_chat
from app.app_settings import AppSettings  # Import AppSettings for app settings
from streamlit_option_menu import option_menu
import app.history as ht
import json
from logging.handlers import (
    RotatingFileHandler,
)  # Import RotatingFileHandler for log rotation

# Define log file and handler
log_file = "app.log"
max_lines = 800  # Threshold for log file reset
handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=0)

# Configure logger
logger = logging.getLogger()

# Remove existing handlers to avoid duplicates
for h in logger.handlers[:]:
    logger.removeHandler(h)

# Add new handler only once
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def check_and_reset_log():
    """Check if the log file has exceeded the line count limit and reset it if necessary."""
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            lines = file.readlines()
            if len(lines) >= max_lines:
                open(log_file, "w").close()  # Reset the file by clearing it


# Call this function at the start of each log cycle or before logging new entries
check_and_reset_log()

# ================= Loading App Settings =================
settings = AppSettings()




# ================= Page Configuration ================
# Remove whitespace padding that is on top of the page
st.markdown(markdown.reomove_padding, unsafe_allow_html=True)

# Define custom CSS styles for the app
st.markdown(
    markdown.app_style,
    unsafe_allow_html=True,
)

# Hide Streamlit menu and footer
st.markdown(markdown.hide_st_style, unsafe_allow_html=True)



# main_container = st.container(height=780, border=False)

#with main_container:
# Main content
st.title("ResearchFlow 🔍")
st.write("Welcome to your personalized Research assistant!")

st.markdown("""___""")

history = ht.ChatHistory()

# Create a container for messages
# Display chat messages
def on_change(key):
    settings.SELECTED_CHAT = st.session_state[key]
    settings.save()
    history.load_chat_into_session_state(settings.SELECTED_CHAT)
    st.session_state["new_chat"] = False
    # state_manager.display_messages(settings.SELECTED_CHAT)

# ================= sidebar Configuration =================
with st.sidebar:

    with st.container(height=500, border=False):
        chat = settings.SELECTED_CHAT
        # Chat interface
        
        chat_history = history.fetch_chat_sessions()
        logging.info(f"Chat History: {chat_history}")
        
        # load a different chat if the selected chat is deleted
        if chat not in chat_history and len(chat_history) > 0:
            chat = chat_history[0]
            settings.SELECTED_CHAT = chat
            settings.save()
            history.load_chat_into_session_state(chat)
            st.session_state["new_chat"] = False

        if len(chat_history) > 0:
            settings.SELECTED_CHAT = option_menu(
                "",
                chat_history,
                menu_icon="chat",
                default_index=chat_history.index(chat),
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "#44475A",
                    },
                    "nav-link": {"font-size": "13px"},
                },
                key="option_menu",
                on_change=on_change,
            )
            # print()
            # print("chat_loaded", st.session_state["chat_loaded"])
            # print("new_chat", st.session_state["new_chat"])
            if not st.session_state["new_chat"] and not st.session_state["chat_loaded"]:
                history.load_chat_into_session_state(settings.SELECTED_CHAT)
                st.session_state["chat_loaded"] = True
                
            
        else:

            settings.SELECTED_CHAT = option_menu(
                "",
                ["New Chat"],
                menu_icon="chat",
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "#44475A",
                    },
                    "nav-link": {"font-size": "13px"},
                },
            )
            st.session_state["new_chat"] = True

    c1, c2 = st.columns(2)
    create_chat_button = c1.button(
        "New", use_container_width=True, key="create_chat_button"
    )

    delete_chat_button = c2.button(
        "Delete", use_container_width=True, key="delete_chat_button"
    )

    def on_change_chat_name():
        new_chat_name = st.session_state["chat_name"]
        history.change_chat_name(settings.SELECTED_CHAT, new_chat_name)
        settings.SELECTED_CHAT = new_chat_name
        settings.save()
        

    st.text_input("change chat name", 
                                key="chat_name", 
                                help="change chat name",
                                value=settings.SELECTED_CHAT, 
                                on_change= on_change_chat_name,
                                )

if create_chat_button:
    st.session_state["new_chat"] = True
    
    st.rerun()
    


if delete_chat_button:
    history.delete_chat_session(settings.SELECTED_CHAT)
    if len(chat_history) > 0:
        selected_chat = chat_history[0]
        settings.SELECTED_CHAT = selected_chat
        settings.save()
    st.session_state["new_chat"] = True
    
    st.rerun()

    


# ================= Main Page Configuration =================

# # check if a file is uploaded and a report for the file has been generated
# file_info = st.session_state["file_info"]
# report = file_info.get("report", "")
# dify_query = st.session_state.get("query", "")

# if file_info.get("name", "") != "" and report != "":
#     dify_query["Query"] = f"Generate a report for : '{file_info.get('title', '')}'"
#     temp_input = json.dumps(dify_query)

#     user_input_id = history.add_user_input(settings.SELECTED_CHAT,  temp_input)
#     app_utils.print_ai_response(report,  settings.SELECTED_CHAT, history, user_input_id)
#     history.load_chat_into_session_state(settings.SELECTED_CHAT)
#     st.session_state["file_info"]["report"] = ""



# Access Streamlit's singleton instance to be able to put the user input box at the bottom of the page
bottom_dg = get_dg_singleton_instance().bottom_dg
# st.html(
#     '''
#         <style>
#             div[aria-label="dialog"]>button[aria-label="Close"] {
#                 display: none;
#             }
#         </style>
#     '''
# )

with bottom_dg:

    file_name  = history.load_file_info(settings.SELECTED_CHAT).get("file_name", "")

    

    if not file_name or st.session_state["new_chat"]:
        upload, col3 = st.columns([0.3, 6])
        with upload:
            upload_btn = st.button("📎", use_container_width=True, on_click=upload_file)
    else:
        logging.info(f"File Name: {file_name}")
        _, uploaded_file, _ = st.columns([0.4, 2, 4])
        _, col3, = st.columns([ 0.3, 6, ]) 
        with uploaded_file:
            st.markdown(
                f"""
                <div style="
                    padding: 10px;
                    border-radius: 8px;
                    background-color: #4CAF50; 
                    color: white; 
                    font-weight: bold;
                    text-align: center;
                    font-size: 18px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    🔎 Uploaded File : {file_name}
                </div>
                """, 
                unsafe_allow_html=True
            )
        
# Place the user input box in the first column
with col3:
    user_input = st.chat_input(
        placeholder="Your message",
        key="chat_input",
        max_chars=2000,
    )


def send_message(u_input : str, selected_chat : str):
        
    """
    Sends a message based on user input, updates the conversation history,
    and retrieves the AI's response.

    Args:
        u_input (str): The input message from the user.
        selected_chat (str): The identifier for the selected chat session.

    Returns:
        None
    """
    
    if st.session_state["new_chat"]:
        new_chat_input =f"Can you generate single chat tilte for this user input: '{u_input}' \n I only need one chat title"
        user_input = app_utils.gen_user_input(selected_chat, new_chat_input, False)
        selected_chat, _ = llm_chat(
            user_input,  settings, []
        )
        
        history.create_chat_session(selected_chat)
        if selected_chat is not None:
            settings.SELECTED_CHAT = selected_chat
            settings.save()
        st.session_state["new_chat"] = False

    
    # if st.session_state["file_info"].get("name", "") != "":
        
    #     file_name = st.session_state["file_info"].get("name", "")
    #     file_id = st.session_state["file_info"].get("id", "")
    #     history.save_file_info(selected_chat, file_name, file_id)
    #     st.session_state["file_id"] = {}


    
    user_input = app_utils.gen_user_input(selected_chat, u_input, False)

    temp_input = json.dumps(user_input)
    # Getting  AI's streamed response
    new_chat_title,response = llm_chat(
        user_input, settings, history.load_chat_history(selected_chat)
    )

    
    # Add user input to the conversation history
    user_input_id = history.add_user_input(selected_chat,  temp_input)
    
    
    app_utils.print_ai_response(response,  selected_chat, history, user_input_id)
    history.load_chat_into_session_state(selected_chat)

    if new_chat_title is None:
        new_chat_title = ""

    if new_chat_title != "":
        settings.SELECTED_CHAT = new_chat_title
        history.change_chat_name(selected_chat, new_chat_title)
        settings.save()
    

    st.rerun()

def regenerate_response(user_input:dict):
    """Regenerate the AI response."""
    _,new_ai_response = llm_chat(
                                user_input, settings, 
                                history.load_chat_history(settings.SELECTED_CHAT)
                            )
    return new_ai_response




# ================= Functions Configuration =================

#with main_container:
if settings.SELECTED_CHAT not in chat_history and len(chat_history) > 0:
    chat = chat_history[0]
    settings.SELECTED_CHAT = chat
    settings.save()
    history.load_chat_into_session_state(chat)
    st.session_state["new_chat"] = False
app_utils.display_messages(settings.SELECTED_CHAT, regenerate_response, history, )#main_container)


# Check conditions and handle inputs
if user_input:
    with st.spinner("Processing...", show_time=True):
        send_message(user_input, settings.SELECTED_CHAT)

    

    



