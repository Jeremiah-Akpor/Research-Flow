import logging
from logging.handlers import RotatingFileHandler
import requests
import json
import pytz
from app.app_utils import throw_error
from app.truncate import trancate
from app.app_settings import AppSettings

# ================= Logging Configuration =================

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

# ================= Initialize Dify Chat =================

def llm_chat(
    user_input: dict,
    settings: AppSettings = None,
    messages: list = [],
):
    logging.info("==============LLM Chat ============")

    dify_api_url: str = settings.DIFY_API_URL
    dify_api_key: str = settings.DIFY_API_KEY
    # new_chat: bool = user_input["new_chat"]
    
    user_input["ChatHistory"] = trancate(user_input["Query"], messages)
    
    # user_input["Paper"] = {}

    headers = {
        "Authorization": f"Bearer {dify_api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "inputs": user_input,
        "response_mode": "blocking",
        "user": "RearchFlow",
        
    }

    logging.info(f"Data: {json.dumps(data, indent=4)}")

    response = ""
    new_chat_title = ""


    try:
        # Perform the API call
        dify_api_url = f"{dify_api_url}/workflows/run"
        logger.info(f"API URL: {dify_api_url}")
        api_call = requests.post(
            dify_api_url, headers=headers, data=json.dumps(data), timeout=180
        )
        logging.info(f"API Call: {api_call}")
        response_text = api_call.text
        logging.info(f"Raw response: {response_text}")

        # Check if the call was successful
        if api_call.status_code == 200:
            # Extract the "answer" part of the response
            data = api_call.json()["data"]
            logging.info(
                f"After initial interaction, api_call: {json.dumps(api_call.json(), indent=4)}"
            )

            # outputs = json.loads(data)

            if data["outputs"]:


                response = data["outputs"].get("response", "")
                new_chat_title = data["outputs"].get("new_chat_title", "")
                graph = data["outputs"].get("graph", "")

                if graph:
                    response = f"{response} \n\n ### Visualization of Database\n{graph}"
            else:
                response = "Dify did not return any response. try rephrasing your query or regenerate your response. or delete the chat and start a new one."

        else:
            logging.error(f"Error {api_call.status_code}: {api_call.text}")
            throw_error(f"Error {api_call.status_code}: {api_call.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"LLM_Chat: An error occurred during the API call: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")


    return new_chat_title,response

    