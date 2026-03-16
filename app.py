import streamlit as st
from src.stages.stage1_input import render_input_form, display_search_summary

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
    search_params = render_input_form()
    
    # If form was submitted successfully
    if search_params:
        display_search_summary(search_params)
        
        # Placeholder for next stage
        st.markdown("---")
        st.info("🔄 Stage 2 (Search Generation) will appear here once implemented.")
        
        # Show raw data for debugging (remove in production)
        with st.expander("Debug: View Raw Parameters"):
            st.json(search_params, expanded=False)

if __name__ == "__main__":
    main()

