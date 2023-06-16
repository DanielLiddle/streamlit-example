import streamlit as st
import pandas as pd
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

# Function to find pages to merge
def find_pages_to_merge(data, position_threshold):
    merge_suggestions = []

    for query in data['query'].unique():
        query_data = data[data['query'] == query]
        query_data = query_data.sort_values(by='position', ascending=True)
        best_page = query_data.iloc[0]

        pages_to_merge = []
        impressions = []
        clicks = []
        positions = []

        for i, row in query_data.iloc[1:].iterrows():
            if row['position'] > position_threshold and best_page['position'] < row['position']:
                pages_to_merge.append(row['page'])
                impressions.append(str(row['impressions']))
                clicks.append(str(row['clicks']))
                positions.append(str(row['position']))

        if pages_to_merge:
            merge_suggestions.append({'Query': query,
                                      'Pages to Merge': ', '.join(pages_to_merge),
                                      'Impressions (Pages to Merge)': ', '.join(impressions),
                                      'Clicks (Pages to Merge)': ', '.join(clicks),
                                      'Positions (Pages to Merge)': ', '.join(positions),
                                      'Number of Pages to Merge': len(pages_to_merge),
                                      'Merge Into': best_page['page'],
                                      'Position (Merge Into)': best_page['position'],
                                      'Impressions (Merge Into)': best_page['impressions'],
                                      'Clicks (Merge Into)': best_page['clicks']})

    return pd.DataFrame(merge_suggestions)


# Streamlit app
st.title('SEO Pages Merger Tool')

# Display instructions
st.markdown("## Instructions")
st.markdown("- Authenticate and authorize using your Google account.")
st.markdown("- Select a website property from Google Search Console.")
st.markdown("- Set the minimum position threshold as required.")
st.markdown("- Click on the 'Fetch and Analyze Data' button to process the data.")

# Set OAuth 2.0 credentials
client_config = {
    "installed": {
        "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "client_secret": "YOUR_CLIENT_SECRET",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}
scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
credentials = flow.run_local_server(port=0)

# Initialize Google Search Console API service
service = build('searchconsole', 'v1', credentials=credentials)

# Fetch list of websites
sites = service.sites().list().execute()

# Select website property
selected_site = st.selectbox("Select website property:", [site['siteUrl'] for site in sites['siteEntry']])

# Set position threshold
position_threshold = st.number_input('Enter Position Threshold:', min_value=1, value=20)

# Fetch and analyze data
if st.button("Fetch and Analyze Data"):
    # Fetch Google Search Console data
    request = {
        'startDate': '2023-01-01',  # You can change this
        'endDate': '2023-06-01',    # You can change this
        'dimensions': ['query', 'page'],
        'rowLimit': 10000           # You can change this
    }
    response = service.searchanalytics().query(siteUrl=selected_site, body=request).execute()

    # Convert data into a DataFrame
    data = pd.DataFrame(response['rows'])
    data['impressions'] = data['impressions'].astype(int)
    data['clicks'] = data['clicks'].astype(int)
    data['position'] = data['position'].astype(float)

    # Analyze data
    result_df = find_pages_to_merge(data, position_threshold)

    # Display results
    if not result_df.empty:
        st.markdown('### Pages To Merge')
        st.dataframe(result_df)
        total_pages_to_merge = result_df['Number of Pages to Merge'].sum()
        st.markdown(f'#### Total Number of Pages to Merge: {total_pages_to_merge}')
        csv = result_df.to_csv(index=False).encode()
        b64 = base64.b64encode(csv).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="pages_to_merge.csv">Download as CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.write('No pages to merge found with the chosen parameters.')
