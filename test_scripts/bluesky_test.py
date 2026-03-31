from atproto import Client
from dotenv import load_dotenv
import os
import requests
import deepl

load_dotenv()

# Authenticate Bluesky credentials
user = os.getenv('BLUESKY_USER')
pw = os.getenv('BLUESKY_PW')
client = Client()
client.login(user, pw)

# Authenticate Deepl credentials
deepl_auth_key = os.getenv("AUTH_KEY")  # replace with your key
deepl_client = deepl.DeepLClient(deepl_auth_key)

# Input query and translate into target langauge
query = '' # replace query in English
t_query = deepl_client.translate_text(query, target_lang="") # Replace target lang: https://developers.deepl.com/docs/getting-started/supported-languages

# Search for posts in target language and translate back into English
results = client.app.bsky.feed.search_posts({'q': str(t_query), 'limit': 10, 'lang': ''}) # Replace lang: https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes - set 2
for post in results.posts:
    text = post.record.text
    t_text = deepl_client.translate_text(text, target_lang="EN-US")
    print(post.author.display_name + ": " + str(t_text) + "\n----------")
    print(post.author.display_name + ": " + str(text) + "\n----------") # Original version for debugging