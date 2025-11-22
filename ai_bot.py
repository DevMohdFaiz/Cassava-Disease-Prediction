import streamlit as st
import os
from groq import Groq
from dotenv import get_key
from typing import List, Dict

@st.cache_data
def load_system_prompt(filepath='system_prompt.md'):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_api_key():
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    if not GROQ_API_KEY:
        try:
            GROQ_API_KEY = st.secrets['GROQ_API_KEY']
        except:
            GROQ_API_KEY = get_key('.env', key_to_get="GROQ_API_KEY")
    return GROQ_API_KEY

GROQ_API_KEY = get_api_key()

def call_groq():
    if Groq is None:
        return None
    if not GROQ_API_KEY:
        raise ValueError("GROQ API KEY not found in environment.\n Ensure you set it properly")
    return Groq(api_key=GROQ_API_KEY)


def build_context(user_query: str, system_prompt: str, predictions_history: List,
                   chat_history: List, max_history_len: int)->List:
    """
    Build context for AI
    
    Args:
        user_query(str): user message
        system_prompt (str)
        predictions_history (str)
        chat_history (list): recent chat
        max_history_len (int): number of recent chats to include
    Returns:
        messages (Dict): full context to be passed to th AI
    """

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'system', 'content': str(predictions_history)},
    ]
    if chat_history:
        recent_chats = chat_history[-max_history_len:]
        messages.extend(recent_chats)
    messages.append({'role': 'user', 'content': user_query})
    return messages


def groq_chat(messages: Dict, model:str= "openai/gpt-oss-120b", max_tokens: int=2048, num_retries:int =3)-> Dict[str, str]:
    """
    Make a call to the Groq API with the query and context

    Args:
        mesages (dict): query with full context
        model (str): AI model to use
        max_tokens (int): maximum number of tokens

    Returns:
        messages (dict): Dictionary with response and metadata
    
    Raises:
        Exception if API call fails
    """
    for attempt in range(1, num_retries+1):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model,
                max_completion_tokens=max_tokens,
                temperature=0.4
            )   
            response_text = chat_completion.choices[0].message.content        
            return {
                'provider': 'groq',
                'model': model,
                'response': response_text,
                "usage": {
                    "prompt_tokens": chat_completion.usage.prompt_tokens,
                    "completion_tokens": chat_completion.usage.completion_tokens,
                    "total_tokens": chat_completion.usage.total_tokens
                    }
                }
        except Exception as e:
            if attempt == num_retries-1:
                raise RuntimeError(f"Groq API call failed after {num_retries} attempts: {str(e)}")
            continue

    raise RuntimeError(f"Unexpected error in Groq API")
