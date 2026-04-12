import requests
from dotenv import load_dotenv
import os
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
import pandas as pd

from utils.common import GroqModel, DeepL, remove_duplicate_links, get_credential

# Load API keys from environment variables or Streamlit secrets
load_dotenv()

class Brave:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def search(self, query, count=20, lang=None, date_range=None):
        url = "https://api.search.brave.com/res/v1/web/search"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": min(count, 20),  # Brave API max count limit is 20
        }
        if lang:
            params["search_lang"] = lang
        if date_range:
            params["freshness"] = date_range
            
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
        
def generate_web_search_queries(search_params):
    groq_key = get_credential("groq_api_key", "GROQ_API_KEY")
    groq_model = GroqModel(groq_key)
    prompt2 = "You are an expert OSINT analyst specializing in human rights investigations. Your task is to generate a list of specific and effective search queries that will be machine-translated and used to find local, grassroots, and domestic sources in the target region that would help gather information relevant to human rights investigations..  Consider the keywords, context, and any other relevant information provided in the search parameters to create queries that are likely to yield useful results. Every query must be designed to surface local and domestic sources only, so append exclusion operators to block international organizations (e.g., -site:un.org -site:amnesty.org -site:hrw.org -site:ohchr.org -site:reuters.com -site:bbc.com) and include a country-code domain hint to bias results toward local sources (e.g., site:.fr)."
    response = groq_model.get_response(
        num_queries=search_params['max_results'],
        prompt=prompt2,
        keywords=search_params['keywords'],
        context=search_params['context']
    )

    return response

def translate_web_search_queries(english_queries, search_params):
    deepl_key = get_credential("deepl_api_key", "DEEPL_API_KEY")
    deepl_client = DeepL(deepl_key)
    translated_queries = []
    
    for query in english_queries['queries']:
        try:
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

def perform_web_searches(translated_queries, search_params, original_queries):
    brave_key = get_credential("brave_api_key", "BRAVE_API_KEY")
    brave_client = Brave(brave_key)
    all_results = []
    
    print("DEBUG: Performing web searches with the following translated queries:")
    print(translated_queries)
    
    for orig_query, trans_query in zip(original_queries, translated_queries):
        try:
            lang_code = "ar" if search_params['languages']['arabic'] else "fr"
            results = brave_client.search(
                query=trans_query,
                count=20,
                    lang=lang_code,
                date_range=f"{search_params['date_range']['start']}to{search_params['date_range']['end']}"
            )
            extracted_results = results.get('web', {}).get('results', [])
            for res in extracted_results:
                res['original_query'] = orig_query
                res['translated_query'] = trans_query
                all_results.append(res)
        except Exception as e:
            st.error(f"Error performing web search: {e}")
            
    df = pd.DataFrame(all_results)
    df = remove_duplicate_links(df)
    
    # Group by queries by sorting them together
    if not df.empty:
        df = df.sort_values(by=['original_query', 'translated_query']).reset_index(drop=True)
        
    return df

@st.cache_data(show_spinner=False)
def web_search(search_params):
    english_queries = generate_web_search_queries(search_params)
    orig_queries = english_queries.get('queries', []) if isinstance(english_queries, dict) else english_queries
    translated_queries = translate_web_search_queries(english_queries, search_params)
    results = perform_web_searches(translated_queries, search_params, orig_queries)
    
    return results, orig_queries, translated_queries