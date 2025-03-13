from typing import List, Dict
import json
import logging

def truncate_helper(messages: List[Dict[str, str]], max_size: int) -> List[Dict[str, str]]:
    """
    Truncate the messages to fit within the given size limit.

    Args:
        messages (List[Dict[str, str]]): The list of messages (history) to truncate.
        max_size (int): The size limit for the messages.

    Returns:
        List[Dict[str, str]]: The truncated list of messages.
    """
    truncated_messages = []
    current_size = 0

    for message in reversed(messages):
        # Calculate the size of the entire message as JSON
        message_size = len(json.dumps(message))
        if current_size + message_size > max_size:
            break
        truncated_messages.append(message)
        current_size += message_size

    return list(reversed(truncated_messages))

context = ""

def trancate(query: str, history: List = []) -> dict:
    """
    Dynamically truncate all components to fit within the total context size.

    Args:
        arg1 (str): JSON string containing query, history, model, and system_prompt.
        history (str): List of  string.

    Returns:
        dict: A dictionary containing the truncated query, model, history, and system_prompt.
    """
    MAX_CONTEXT_SIZE = 6000



    # Calculate the size of all components
    query_size = len(query)
    history_size = sum(len(json.dumps(msg)) for msg in history)
    logging.info(f"History size: {history_size}")
    total_size = query_size  + history_size

    # Determine how much needs to be truncated
    if total_size > MAX_CONTEXT_SIZE:
        excess_size = total_size - MAX_CONTEXT_SIZE

        # Truncate history first
        if excess_size > 0 and history_size > 0:
            history_space = max(0, history_size - excess_size)
            history = truncate_helper(history, history_space)
            excess_size -= (history_size - sum(len(json.dumps(msg)) for msg in history))

    return json.dumps(history, indent=2)
