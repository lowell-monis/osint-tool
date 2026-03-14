import os
from urllib import response
from urllib.parse import quote_plus
from dotenv import load_dotenv, find_dotenv
from groq import Groq
import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

NUM_QUERIES = 1
NUM_RESULTS = 10

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except StreamlitSecretNotFoundError:
        GROQ_API_KEY = None
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
if not BRAVE_API_KEY:
    try:
        BRAVE_API_KEY = st.secrets.get("BRAVE_API_KEY")
    except StreamlitSecretNotFoundError:
        BRAVE_API_KEY = None
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not SERPER_API_KEY:
    try:
        SERPER_API_KEY = st.secrets.get("SERPER_API_KEY")
    except StreamlitSecretNotFoundError:
        SERPER_API_KEY = None



class LLMModel:
    def __init__(self, model: str, api_key: str) -> None:
        self.client = Groq(api_key=api_key)
        self.model = model

    def get_response(self, prompt: str, user_input: str):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
        )

    def get_response_message(self, prompt: str, user_input: str) -> str:
        response = self.get_response(prompt, user_input)
        return response.choices[0].message.content

def generate_search_queries(model: LLMModel, user_input: str, prompt: str) -> list[str]:
    raw_queries = model.get_response_message(prompt, user_input)
    return [line.strip("- ").strip() for line in raw_queries.splitlines() if line.strip()]

class BraveSearch():
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query):
        url = "https://api.search.brave.com/res/v1/web/search"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query
        }

        response = requests.get(url, headers=headers, params=params)
        return response.json()

class SerperSearch():
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query):
        url = "https://google.serper.dev/search"

        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            "q": query
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        return response.json()



st.header("CrossLing")
with st.form("search_form"):
    search_input = st.text_input(
        "Search for articles, posts, and more",
        placeholder="Search",
    )
    submitted = st.form_submit_button("Search")

prompt = (
    f"Generate {NUM_QUERIES} search queries from the user's question with a focus on "
    "underreported political situations. One per line, only plain text, and no numbered/bulleted list."
)

if submitted and search_input:
    if not GROQ_API_KEY:
        st.error("Missing GROQ_API_KEY. Add it to Streamlit secrets or environment variables.")
    elif not BRAVE_API_KEY:
        st.error("Missing BRAVE_API_KEY. Add it to Streamlit secrets or environment variables.")
    elif not SERPER_API_KEY:
        st.error("Missing SERPER_API_KEY. Add it to Streamlit secrets or environment variables.")
    else:
        model = LLMModel("llama-3.1-8b-instant", GROQ_API_KEY)
        queries = generate_search_queries(model, search_input, prompt)
        search_engine = BraveSearch(BRAVE_API_KEY)
        #search_engine = SerperSearch(SERPER_API_KEY) ----- NOT YET IMPLEMENTED

        st.subheader("Search Results")
        for idx, query in enumerate(queries, start=1):
            if idx > 1:
                continue
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            st.markdown(f"{idx}. [{query}]({search_url})")
            search_results = search_engine.search(query)
            with st.expander(f"Results for query {idx}"):
                if search_results.get("web", {}).get("results"):
                    for i in range(NUM_RESULTS):
                        result = search_results["web"]["results"][i]
                        st.markdown(f"**{result['title']}**")
                        st.markdown(f"URL: {result['url']}")
                        st.markdown(f"Description: {result['description']}")

elif submitted and not search_input:
    st.warning("Enter a search topic first.")
