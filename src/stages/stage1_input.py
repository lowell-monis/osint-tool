import streamlit as st
from datetime import datetime, timedelta

def render_input_form(platform):
    """
    Renders the user input form for CrossLing.
    Returns a dictionary with user inputs.
    """
    
    st.header("🔍 CrossLing: Multilingual OSINT Search")
    st.markdown("Enter your search parameters below to find human rights evidence across languages.")
    
    # Initialize session state for form data if it doesn't exist
    if 'search_params' not in st.session_state:
        st.session_state.search_params = None
    
    with st.form(key=platform):
        # 1. English Keywords (Required)
        st.subheader("Search Terms")
        keywords = st.text_area(
            "English Keywords *",
            placeholder="e.g., migrant smuggling Libya truck, Milei economic protests Argentina",
            help="Enter keywords or phrases in English. Separate multiple terms with commas.",
            height=100
        )
        
        # 2. Target Languages (Required)
        st.subheader("Target Languages")
        col1, col2 = st.columns(2)
        
        with col1:
            arabic = st.checkbox("Arabic", value=True)
        with col2:
            french = st.checkbox("French", value=False)
        
        # 3. Optional Context
        st.subheader("Context (Optional but Recommended)")
        context = st.text_area(
            "What are you looking for?",
            placeholder="e.g., Looking for Facebook posts showing vehicles transporting migrants in Bani Walid, Libya between 2015-2019",
            help="Provide context to help generate better search queries. Include locations, time periods, specific events, or types of evidence you're seeking.",
            height=120
        )
        
        # 4. Date Range
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        
        default_start = datetime.now() - timedelta(days=365)
        default_end = datetime.now()
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=default_start,
                min_value=datetime(2000, 1, 1),
                max_value=datetime.now()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=datetime(2000, 1, 1),
                max_value=datetime.now()
            )
        
        # 5. Media Type Preferences
        st.subheader("Media Types to Search")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            include_text = st.checkbox("Text (articles, posts)", value=True)
        with col2:
            include_images = st.checkbox("Images", value=True)
        with col3:
            include_videos = st.checkbox("Videos", value=False)
        
        # 6. Advanced Options (Collapsible)
        with st.expander("Advanced Options"):
            max_results = st.slider(
                "Maximum number of queries",
                min_value=5,
                max_value=50,
                value=15,
                step=5,
                help="Limit results to stay within API quotas"
            )
            
            platforms = st.multiselect(
                "Platforms to search",
                options=["Web", "News", "Twitter/X", "Facebook", "TikTok (experimental)"],
                default=["Web", "News", "Twitter/X", "Facebook"],
                help="Select which platforms to search. TikTok is experimental and may not work reliably."
            )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Generate Searches", use_container_width=True)

        if submitted:
            # Validate inputs
            errors = []
            
            if not keywords.strip():
                errors.append("❌ Keywords are required")
            
            if not arabic and not french:
                errors.append("❌ Select at least one target language")
            
            if start_date > end_date:
                errors.append("❌ Start date must be before end date")
            
            if not include_text and not include_images and not include_videos:
                errors.append("❌ Select at least one media type")
            
            if errors:
                for error in errors:
                    st.error(error)
                return None
            
            # Package data
            search_params = {
                'keywords': keywords.strip(),
                'languages': {
                    'arabic': arabic,
                    'french': french
                },
                'context': context.strip() if context else None,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'media_types': {
                    'text': include_text,
                    'images': include_images,
                    'videos': include_videos
                },
                'max_results': max_results,
                'platforms': platforms,
                'timestamp': datetime.now()
            }
            
            # Store in session state
            st.session_state.search_params = search_params
            
            # Success message
            st.success("✅ Search parameters validated! Proceeding to query generation...")
            
            return search_params
    
    return None


def display_search_summary(params):
    """
    Display a summary of the search parameters for user confirmation.
    """
    if params is None:
        return
    
    st.subheader("📋 Search Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Keywords", params['keywords'][:50] + "..." if len(params['keywords']) > 50 else params['keywords'])
        
        langs = []
        if params['languages']['arabic']:
            langs.append("Arabic")
        if params['languages']['french']:
            langs.append("French")
        st.metric("Languages", ", ".join(langs))
    
    with col2:
        date_str = f"{params['date_range']['start'].strftime('%Y-%m-%d')} to {params['date_range']['end'].strftime('%Y-%m-%d')}"
        st.metric("Date Range", date_str)
        
        st.metric("Platforms", f"{len(params['platforms'])} selected")
    
    if params['context']:
        with st.expander("View Context"):
            st.info(params['context'])