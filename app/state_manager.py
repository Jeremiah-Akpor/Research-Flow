import streamlit as st
import logging  # Import logging for logging purposes


from logging.handlers import (
    RotatingFileHandler,
)


# Define log file and handler
log_file = "app.log"
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


def initialize_state():
    """Initialize session state variables."""
    
    if "messages" not in st.session_state:
        # Load DataFrame or create an empty one
     
        st.session_state["messages"] = [
            {
                "role": "ai",
                "content": "Hello! I am here to help you with your Research. How can I help you today?",
                "version": 0,
                "user_input_id": ""
            }
        ]


    
    if "new_chat" not in st.session_state:
        st.session_state["new_chat"] = False
    
    
    
    # ================== Needed for Regenerating LLM Response ==================
    if "chat_loaded" not in st.session_state:
        st.session_state["chat_loaded"] = False

    # ================== Needed for switching between LLM Response version for a particular user input ==================

    if "version_idx" not in st.session_state:
        st.session_state["version_idx"] = 0
    
    if "copied" not in st.session_state: 
        st.session_state.copied = []
    
    if "file_info" not in st.session_state:
        st.session_state["file_info"] = {"name" : "", "id" : "", "report": ""}
    
def update_messages(messages):
    """Update messages list in session state."""
    st.session_state["messages"].append(messages)



