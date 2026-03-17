import os
from urllib.parse import quote_plus
#from dotenv import load_dotenv, find_dotenv

from groq import Groq
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

#load_dotenv(find_dotenv())

# need to set environment variables before running GROQ_API_KEY

class LLMModel:
    def __init__(self, model: str, api_key = "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") -> None:
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


st.header("CrossLing")
with st.form("search_form"):
    search_input = st.text_input(
        "Search for articles, posts, and more",
        placeholder="Search",
    )
    submitted = st.form_submit_button("Search")

os.environ['GROQ_API_KEY'] = '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'
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except StreamlitSecretNotFoundError:
        api_key = None
prompt = (
    "Generate 10 search queries from the user's question with a focus on "
    "underreported political situations. One per line, no extra text."
)

if submitted and search_input:
    if not api_key:
        st.error("Missing GROQ_API_KEY. Add it to Streamlit secrets or environment variables.")
    else:
        model = LLMModel("llama-3.1-8b-instant", api_key)
        queries = generate_search_queries(model, search_input, prompt)

        st.subheader("Search Results")
        for idx, query in enumerate(queries, start=1):
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            st.markdown(f"{idx}. [{query}]({search_url})")

elif submitted and not search_input:
    st.warning("Enter a search topic first.")

