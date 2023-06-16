#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip install streamlit')


# In[4]:


import streamlit as st
import pandas as pd
import numpy as np

# Title of the app
st.title("SEO Landing Page Merger Tool")

# Upload CSV data
file_upload = st.file_uploader("Choose a CSV file", type="csv")

# Instructions
st.markdown("Upload a CSV file with the columns: 'Query', 'Landing Page', 'Url Clicks', 'Impressions', 'Average Position'. The app will process the data and show you which landing pages can be merged based on the specified criteria.")

# If a file is uploaded
if file_upload is not None:
    # Load data
    data = pd.read_csv(file_upload)
    
    # Show initial data in table format
    st.subheader("Initial Data")
    st.table(data.head())

    # Logic for merging pages
    min_impressions = st.sidebar.slider("Minimum Impressions", 1, 1000, 500)
    position_threshold = st.sidebar.slider("Position Threshold", 1, 100, 10)
    
    data_filtered = data[data['Impressions'] >= min_impressions]
    
    merge_recommendations = []

    for query in data_filtered['Query'].unique():
        relevant_pages = data_filtered[data_filtered['Query'] == query]
        best_page = relevant_pages.loc[relevant_pages['Average Position'].idxmin()]
        
        for index, page in relevant_pages.iterrows():
            if page['Average Position'] > best_page['Average Position'] and page['Average Position'] > position_threshold:
                merge_recommendations.append({
                    'Query': query,
                    'Merge Into': best_page['Landing Page'],
                    'Page to Merge': page['Landing Page'],
                    'Impressions': page['Impressions'],
                    'Average Position': page['Average Position'],
                    'Url Clicks': page['Url Clicks']
                })

    if merge_recommendations:
        recommendations_df = pd.DataFrame(merge_recommendations)
        # Show recommendations
        st.subheader("Merge Recommendations")
        st.table(recommendations_df)
    else:
        st.warning("No merge recommendations found with the current criteria.")

# You can add more features like buttons, charts, images, etc.


# In[ ]:




