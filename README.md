# CrossLing

## Getting Started

### Setting Up API Keys and Credentials

1. Brave Search API Key
    - Navigate to https://api-dashboard.search.brave.com/register and create an account.
    - Go to the "Plans" section and select a "Search" plan, filling in the required information as you see fit.
    - Next, go to the "API Keys" section and click "Add API Key". Fill in the information using the Search plan you just created, and copy the generated API key (store it somewhere safe, as you will need it later).
    - Note: I'd highly recommend using a lower tier plan first and scaling up as needed. Also, I'd recommend setting up a limit for API usage under the "Usage Limits" section to avoid any unexpected charges.

2. DeepL API Key
    - Navigate to https://www.deepl.com/en/signup?cta=checkout&is_api=true&productId=api-developer and create an account, making sure the "Developer" plan is selected.
    - Go to "Account" and then go to "API Keys & Limits". Create an API key, and copy the generated API key (store it somewhere safe, as you will need it later).
    - Note: I'd highly recommend using a lower tier plan first and scaling up as needed. Also, I'd recommend setting up a limit for API usage under the "Usage Limits" section to avoid any unexpected charges if you choose a higher level plan.

3. Groq API Key
    - Navigate to https://console.groq.com and create an account.
    - Go to the "API Keys" section and create an API key, and copy the generated API key (store it somewhere safe, as you will need it later).
    - Note: I'd highly recommend using a lower tier plan first and scaling up as needed. Also, I'd recommend setting up a limit for API usage under the "Limits" section to avoid any unexpected charges if you choose a higher level plan than the Free one.

4. Bluesky Credentials
    - Navigate to https://bsky.app/ and create an account.
    - Save your username and password somewhere safe, as you will need them later.

### Using CrossLing

- Navigate to https://crossling.streamlit.app/ to open the CrossLing web application.
- Input your API keys and credentials into their respective fields on the left-hand sidebar.
- Select either "Web" or "Bluesky" as your search method.
- Search keywords (in English), the target language, any potential context you want to include, the desired date range for the search, and the number of queries you want to generate.
    - Note: The number of queries will be the biggest factor contributing to your API usage.
- Click "Generate Searches" to initiate the search process.

- CrossLing will generate a list of search results based on your input. You can also view the input parameters, generated/translated queries, and even download the results as a CSV file for further analysis!

## Contact

For any questions or support, please contact the development team at gunnjack@msu.edu
