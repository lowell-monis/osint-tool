# Experimental script for testing search functionality.

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def brave_search():
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        #"X-Subscription-Token": os.getenv("BRAVE_API_KEY")
    }
    params = {
        "q": "artificial intelligence"
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json()

    # Print the first search result
    if results.get("web", {}).get("results"):
        first_result = results["web"]["results"][0]
        print(f"Title: {first_result['title']}")
        print(f"URL: {first_result['url']}")
        print(f"Description: {first_result['description']}")
        
def serper_search():
    url = "https://google.serper.dev/search"

    payload = {
    "q": "artificial intelligence"
    }
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    print(response.text)