import streamlit as st
from src.stages.stage1_input import render_input_form, display_search_summary
from src.stages.stage2_search import web_search
from src.stages.stage4_output import display_results
import deepl

# Page config
st.set_page_config(
    page_title="CrossLing - Multilingual OSINT",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.title("CrossLing")
    st.markdown("**Multilingual OSINT for Human Rights**")
    st.markdown("---")
    st.markdown("### Current Stage")
    st.info("Stage 1: User Input")
    st.markdown("---")
    st.markdown("### Pipeline Status")
    st.markdown("✅ Stage 1: Input")
    st.markdown("⏳ Stage 2: Search Generation")
    st.markdown("⏳ Stage 3: Scraping")
    st.markdown("⏳ Stage 4: Output")

# Main content
def main():
    # Render input form
    params = render_input_form()
    
    # If form was submitted successfully
    if params:
        display_search_summary(params)
        
        # Perform web search
        results, original_queries, translated_queries = web_search(params)
        
        # Display results
        display_results(results, params, original_queries, translated_queries)
        
        # Show raw data for debugging (remove in production)
        with st.expander("Debug: View Raw Parameters"):
            st.json(params, expanded=False)

if __name__ == "__main__":
    main()
