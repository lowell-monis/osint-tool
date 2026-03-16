from atproto import Client
from dotenv import load_dotenv
import os
import requests
import deepl

load_dotenv()

# Put account details in .env
user = os.getenv('BLUESKY_USER')
pw = os.getenv('BLUESKY_PW')

# Put deepl details in .env
deepl_auth_key = os.getenv("AUTH_KEY")  # replace with your key
deepl_client = deepl.DeepLClient(deepl_auth_key)

# Log in to Bluesky API
client = Client()
client.login(user, pw)

# Input query and translate into target langauge
query = 'Canadiens' # replace query in English
t_query = deepl_client.translate_text(query, target_lang="FR") # https://developers.deepl.com/docs/getting-started/supported-languages

# Search for posts in target language and translate back into English
results = client.app.bsky.feed.search_posts({'q': query, 'limit': 10, 'lang': 'fr'}) # https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes - set 2
for post in results.posts:
    text = post.record.text
    t_text = deepl_client.translate_text(text, target_lang="EN-US")
    print(post.author.display_name + ": " + str(t_text) + "\n----------")
    print(post.author.display_name + ": " + str(text) + "\n----------") # Original version for debugging