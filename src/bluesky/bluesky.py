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
import traceback
import pandas as pd
from utils.common import GroqModel, DeepL, remove_duplicate_links, get_credential

# Load API keys from environment variables or Streamlit secrets
load_dotenv()

# Set parameters for web search
GROQ_MODEL = "llama-3.1-8b-instant"


# PRINT DEBUGGING INFO ABOUT EVERYTHING HAPPENING TO FIGURE OUT WHAT'S GOING WRONG WITH THE WEB SEARCH STAGE

def get_bluesky_client():
    user = get_credential("bluesky_user", "BLUESKY_USER")
    pw = get_credential("bluesky_pw", "BLUESKY_PW")
    client = Client()
    if user and pw:
        try:
            client.login(user, pw)
            return client
        except Exception as e:
            st.error(f"Bluesky login failed: {e}")
    else:
        st.error("Missing Bluesky credentials.")
    return None

def generate_bluesky_search_queries(search_params):
    groq_key = get_credential("groq_api_key", "GROQ_API_KEY")
    groq_model = GroqModel(groq_key)
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
    deepl_key = get_credential("deepl_api_key", "DEEPL_API_KEY")
    deepl_client = DeepL(deepl_key)
    translated_queries = []
    
    for query in english_queries['queries']:
        if isinstance(query, str) and query.strip():
            try:
                print(f"DEBUG: Translating query: {query}")
                translated_query = deepl_client.translate(
                    text=query,
                    target_lang="AR" if search_params['languages']['arabic'] else "FR"
                )
                if isinstance(translated_query, str):
                    translated_queries.append(translated_query)
                else:
                    translated_queries.append(query)
            except Exception as e:
                st.error(f"Error translating query: {e}")
                translated_queries.append(query)

    return translated_queries

def perform_bluesky_searches(translated_queries, search_params, original_queries):
    client = get_bluesky_client()
    if not client:
        return pd.DataFrame()
        
    checklimit = 0
    posts = []
    for orig_query, trans_query in zip(original_queries, translated_queries):
        try:
            results = client.app.bsky.feed.search_posts({'q': str(orig_query), 'since': str(search_params['date_range']['start'].strftime('%Y-%m-%dT%H:%M:%SZ')), 'until': str(search_params['date_range']['end'].strftime('%Y-%m-%dT%H:%M:%SZ'))})
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
                    "url": url,
                    "original_query": orig_query,
                    "translated_query": trans_query
                }
                posts.append(entry)
        except Exception as e:
            st.error(f"Error performing Bluesky search: {e}")
            
    df = pd.DataFrame(posts)
    df = remove_duplicate_links(df)
    
    # Group by queries by sorting them together
    if not df.empty:
        df = df.sort_values(by=['original_query', 'translated_query']).reset_index(drop=True)
        
    return df

@st.cache_data(show_spinner=False)
def bluesky_search(search_params):
    english_queries = generate_bluesky_search_queries(search_params)
    orig_queries = english_queries.get('queries', []) if isinstance(english_queries, dict) else english_queries
    translated_queries = translate_bluesky_search_queries(english_queries, search_params)
    results = perform_bluesky_searches(translated_queries, search_params, orig_queries)
    
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