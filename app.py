import streamlit as st
from src.stages.stage1_input import render_input_form, display_search_summary
from src.stages.stage2_search import web_search
from src.bluesky.bluesky import bluesky_search
from src.stages.stage4_output import display_results
import deepl

# Page config
st.set_page_config(
    page_title="CrossLing - Multilingual OSINT",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Tabs
tab1, tab2 = st.tabs(["Web", "Bluesky"])
# with tab1:
#     st.header("Web")
# with tab2:
#     st.header("Bluesky")

# Sidebar
# Sidebar
with st.sidebar:
    st.title("CrossLing")
    st.markdown("**Multilingual OSINT for Human Rights**")
    st.markdown("---")
    
    st.subheader("🔑 API Keys & Credentials")
    
    # Initialize session state for all keys
    defaults = {
        "brave_api_key": "",
        "deepl_api_key": "",
        "bluesky_user": "",
        "bluesky_pw": "",
        "groq_api_key": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    st.text_input("Brave API Key", type="password", key="brave_api_key")
    st.text_input("DeepL API Key", type="password", key="deepl_api_key")
    st.text_input("Groq API Key", type="password", key="groq_api_key")
    
    st.markdown("**Bluesky**")
    st.text_input("Username", key="bluesky_user")
    st.text_input("Password", type="password", key="bluesky_pw")

    # Status indicators
    st.markdown("---")
    required_keys = {
        "Brave": "brave_api_key",
        "DeepL": "deepl_api_key",
        "Groq": "groq_api_key",
        "Bluesky": "bluesky_user",
    }
    all_set = all(st.session_state[v] for v in required_keys.values())
    if all_set:
        st.success("All credentials set ✓")
    else:
        missing = [k for k, v in required_keys.items() if not st.session_state[v]]
        st.warning(f"Missing: {', '.join(missing)}")
    

# Main content
def main():
    with tab1:
        # Render input form
        render_input_form("web")
        
        # Check session state instead of direct form return
        search_params = st.session_state.get("web_search_params")
        if search_params:
            display_search_summary(search_params)
            
            
            # Perform web search
            results, original_queries, translated_queries = web_search(search_params)
            
            # Display results
            display_results(results, search_params, original_queries, translated_queries, platform="websearch")
            
            # Show raw data for debugging (remove in production)
            with st.expander("Debug: View Raw Parameters"):
                st.json(search_params, expanded=False)
    with tab2:
        # Render input form
        render_input_form("bsky")
        
        # Check session state instead of direct form return
        search_params = st.session_state.get("bsky_search_params")
        if search_params:
            display_search_summary(search_params)
            
            
            # Perform web search
            results, original_queries, translated_queries = bluesky_search(search_params)
            
            # Display results
            display_results(results, search_params, original_queries, translated_queries, platform="bluesky")
            
            # Show raw data for debugging (remove in production)
            with st.expander("Debug: View Raw Parameters"):
                st.json(search_params, expanded=False)

if __name__ == "__main__":
    main()
