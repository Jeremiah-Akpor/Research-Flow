import json
import streamlit as st  # Import Streamlit for creating the web app
import app.app_utils as app_utils  # Import custom utility functions

from app.app_settings import AppSettings
import app.markdown as markdown  # Import custom markdown styles
import requests
import logging
from logging.handlers import RotatingFileHandler
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



# ================= Loading App Settings =================

settings = AppSettings()


# ================= Page Configuration =================
# Remove whitespace padding that is on top of the page
st.markdown( markdown.reomove_padding,unsafe_allow_html=True)

# Define custom CSS styles for the app
st.markdown(markdown.app_style,unsafe_allow_html=True,)

# Hide Streamlit menu and footer
st.markdown(markdown.hide_st_style, unsafe_allow_html=True)

st.title("ReaserchFlow 🔍 Setting")  # Set the title of the app
st.write("Your Local Personal Research Assistant!")  # Display a welcome message




# ================= Dify URL Settings =================
settings.DIFY_API_URL = st.text_input(
    "Enter the URL of Dify API",
    value=settings.DIFY_API_URL,
)  # Text input for entering the URL of Dify API

# ====================== Reset dify conversation =============================



if api_key := st.text_input(
    "Enter the Access Key of Dify API",
    value=settings.DIFY_API_KEY,
    type="password",
    # on_change=reset_conversation_id
) : 
    settings.DIFY_API_KEY = api_key
    settings.save()

    
            
# ================= Save Settings =================

if st.sidebar.button(
    "Save Settings", use_container_width=True, 
):  # Save settings button in the sidebar
    settings.save()  # Save the settings to the database
    st.success("Settings saved successfully!")  # Display success message
