import streamlit as st

st.title("SEO Assistant")

user_query = st.text_input("What is your question?")

if user_query:
    st.write("It depends.")
