import streamlit as st
import app.state_manager as state_manager
import os
import logging
from logging.handlers import (
    RotatingFileHandler,
)  # Import RotatingFileHandler for log rotation

# Define log file and handler
log_file = "app.log"
max_lines = 1500  # Threshold for log file reset
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


# ================= Page Configuration =================
st.set_page_config(
    page_icon="🔍", layout="wide", page_title="ResearchFlow"
)  # Set the page icon and layout





# Initialize session state
state_manager.initialize_state()



# ================= Load Pages =================
settings_page = st.Page("app/settings.py", title="Settings", icon=":material/settings:")




chat = st.Page("app/chat.py", title="Chat", icon=":material/chat:")



pages = [chat, settings_page ]

if len(pages) > 0:
    pg = st.navigation(pages, expanded=False)


pg.run()