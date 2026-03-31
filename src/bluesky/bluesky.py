import deepl
import requests
from dotenv import load_dotenv
import os
import json
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from groq import Groq as GroqClient
from datetime import datetime, timedelta
from atproto import Client

# Load API keys from environment variables or Streamlit secrets
load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if not DEEPL_API_KEY:
    try:
        DEEPL_API_KEY = st.secrets.get("DEEPL_API_KEY")
    except StreamlitSecretNotFoundError:
        DEEPL_API_KEY = None
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except StreamlitSecretNotFoundError:
        GROQ_API_KEY = None

BLUESKY_USER = os.getenv('BLUESKY_USER')
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except StreamlitSecretNotFoundError:
        GROQ_API_KEY = None

BLUESKY_PW = os.getenv('BLUESKY_PW')
if not BLUESKY_PW:
    try:
        BLUESKY_PW = st.secrets.get("BLUESKY_PW")
    except StreamlitSecretNotFoundError:
        BLUESKY_PW = None

BLUESKY_CLIENT = Client()
BLUESKY_CLIENT.login(BLUESKY_USER, BLUESKY_PW)

# Set parameters for web search
GROQ_MODEL = "llama-3.1-8b-instant"


# PRINT DEBUGGING INFO ABOUT EVERYTHING HAPPENING TO FIGURE OUT WHAT'S GOING WRONG WITH THE WEB SEARCH STAGE

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
        
def generate_bluesky_search_queries(search_params):
    groq_model = GroqModel(GROQ_API_KEY)
    prompt = """
You are an expert OSINT analyst. Based on the following search parameters, generate a list of specific and effective Bluesky search queries that would help gather information relevant to human rights investigations. The queries should be designed to find a variety of sources, including news articles, social media posts, reports, and other online content. Consider the keywords, context, and any other relevant information provided in the search parameters to create queries that are likely to yield useful results. Make sure the queries are optimized for Bluesky's search functionality.
- Enclose with double quotes to find specific phrases
- Prefix hashtags with #
- Search for a handle to find posts that mention the user
- Paste URLs to search for posts that contain the URL, prefix the URL with domain: to find posts that share a domain
- Use lang: followed by the 2 character ISO code to search for posts in a specific language
"""
    
    response = groq_model.get_response(
        num_queries=search_params['max_results'],
        prompt=prompt,
        keywords=search_params['keywords'],
        context=search_params['context']
    )

    return response

def translate_bluesky_search_queries(english_queries, search_params):
    deepl_client = DeepL(DEEPL_API_KEY)
    translated_queries = []
    
    for query in english_queries['queries']:
        try:
            if query:
                print(f"DEBUG: Translating query: {query}")
                translated_query = deepl_client.translate(
                    text=query,
                    target_lang="AR" if search_params['languages']['arabic'] else "FR"
                )
                translated_queries.append(translated_query)
        except Exception as e:
            st.error(f"Error translating query: {e}")
            translated_queries.append(query)

    return translated_queries

def perform_bluesky_searches(queries, search_params):
    checklimit = 0
    posts = []
    for query in queries:
        try:
            results = BLUESKY_CLIENT.app.bsky.feed.search_posts({'q': str(query), 'since': str(search_params['date_range']['start'].strftime('%Y-%m-%dT%H:%M:%SZ')), 'until': str(search_params['date_range']['end'].strftime('%Y-%m-%dT%H:%M:%SZ'))})
            for post in results.posts:
                if not post.record.text:
                    text = " "
                else:
                    text = post.record.text
                rkey = post.uri.split("/")[-1]
                url = f"https://bsky.app/profile/{post.author.handle}/post/{rkey}"
                print(post.author.display_name + " (" + post.author.handle + ")"+ ": " + str(text) + "\n" + url +"\n----------") # for debugging
                entry = {
                    "title": post.author.display_name + " (" + post.author.handle + ")",
                    "description": post.record.text,
                    "url": url
                }
                posts.append(entry)
        except Exception as e:
            st.error(f"Error translating query: {e}")
    return posts

def bluesky_search(search_params):
    english_queries = generate_bluesky_search_queries(search_params)
    translated_queries = translate_bluesky_search_queries(english_queries, search_params)
    results = perform_bluesky_searches(translated_queries, search_params)
    
    orig_queries = english_queries.get('queries', []) if isinstance(english_queries, dict) else english_queries
    return results, orig_queries, translated_queries

# ---DEBUGGING---
# search_params = {
#                 'keywords': "Libya",
#                 'languages': {
#                     'arabic': True,
#                     'french': False
#                 },
#                 'context': None,
#                 'date_range': {
#                     'start': datetime(2025, 3, 30),
#                     'end': datetime(2026, 3, 30)
#                 },
#                 'media_types': {
#                     'text': True,
#                     'images': False,
#                     'videos': False
#                 },
#                 'max_results': 10,
#                 'platforms': "News",
#                 'timestamp': datetime.now()
#             }
# bluesky_search(search_params)
# queries = generate_bluesky_search_queries(search_params)
# t_queries = translate_bluesky_search_queries(queries, search_params)
# bluesky_posts = perform_bluesky_searches(t_queries, search_params)

# print(bluesky_posts)