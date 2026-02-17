import streamlit as st

st.header("osint-tool")

text_input = st.text_input(
    "Search for articles, posts, and more",
    placeholder="Search",
)

if text_input:
    st.write("You entered: ", text_input)