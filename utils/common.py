import json
import deepl
import os
import pandas as pd
import streamlit as st
from groq import Groq as GroqClient

def get_credential(state_key: str, env_key: str):
    """
    Consolidated method to get API keys and credentials.
    Prioritizes Streamlit session state (user input), then environment variables (.env).
    """
    # 1. Try session state (from Streamlit sidebar)
    val = st.session_state.get(state_key)
    if val:
        return val
        
    # 2. Try environment variable (from .env)
    val = os.getenv(env_key)
    if val:
        return val
        
    # 3. Try Streamlit secrets (fallback for deployed apps)
    try:
        val = st.secrets.get(env_key)
        if val:
            return val
    except Exception:
        pass
        
    return None

class GroqModel:
    def __init__(self, api_key):
        self.client = GroqClient(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        
    def get_response(self, num_queries: int, prompt: str, keywords: str, context: str = None):
        user_content = f"Keywords: {keywords}\n"
        if context:
            user_content += f"Context: {context}\n"

        system_prompt = (
            f"{prompt}\n"
            f"Generate exactly {num_queries} search queries.\n"
            "Return the queries as a JSON object with a single key 'queries' which is a list of strings. For example: {\"queries\": [\"query 1\", \"query 2\"]}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error generating search queries from LLM: {e}")
            return {"queries": []}

class DeepL:
    def __init__(self, api_key):
        self.client = deepl.DeepLClient(api_key)
        
    def translate(self, text: str, target_lang: str) -> str:
        try:
            response = self.client.translate_text(text, target_lang=target_lang)
            return response.text
        except Exception as e:
            st.error(f"Error translating text with DeepL: {e}")
            return text

def remove_duplicate_links(df):
    if df.empty or 'url' not in df.columns:
        return df
    return df.drop_duplicates(subset=['url']).reset_index(drop=True)
