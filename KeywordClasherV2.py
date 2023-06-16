import streamlit as st
import pandas as pd
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime


def get_authorization_url(client_id, client_secret):
    oauth2_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "scopes": ["https://www.googleapis.com/auth/webmasters.readonly"]
        }
    }
    flow = Flow.from_client_config(oauth2_config, scopes=oauth2_config['installed']['scopes'], redirect_uri=oauth2_config['installed']['redirect_uris'][0])
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url, flow


def exchange_code_for_credentials(flow, authorization_response):
    flow.fetch_token(code=authorization_response)
    return flow.credentials


def find_pages_to_merge(data, position_threshold):
    merge_suggestions = []

    for query in data['Query'].unique():
        query_data = data[data['Query'] == query]
        query_data = query_data.sort_values(by='Average Position', ascending=True)
        best_page = query_data.iloc[0]

        pages_to_merge = []
        impressions = []
        url_clicks = []
        average_positions = []

        for i, row in query_data.iloc[1:].iterrows():
            if row['Average Position'] > position_threshold and best_page['Average Position'] < row['Average Position']:
                pages_to_merge.append(row['Landing Page'])
                impressions.append(str(row['Impressions']))
                url_clicks.append(str(row['Url Clicks']))
                average_positions.append(str(row['Average Position']))

        if pages_to_merge:
            merge_suggestions.append({'Query': query,
                                      'Pages to Merge': ', '.join(pages_to_merge),
                                      'Impressions (Pages to Merge)': ', '.join(impressions),
                                      'Url Clicks (Pages to Merge)': ', '.join(url_clicks),
                                      'Average Positions (Pages to Merge)': ', '.join(average_positions),
                                      'Number of Pages to Merge': len(pages_to_merge),
                                      'Merge Into': best_page['Landing Page'],
                                      'Average Position (Merge Into)': best_page['Average Position'],
                                      'Impressions (Merge Into)': best_page['Impressions'],
                                      'Url Clicks (Merge Into)': best_page['Url Clicks']})

    return pd.DataFrame(merge_suggestions)


st.title('Google Search Console Page Merger Tool')

st.markdown('## Instructions')
st.markdown('- Add your Google Cloud Client ID and Client Secret.')
st.markdown('- Authorize the app to access your Google Search Console data.')
st.markdown('- Select your site from the dropdown list.')
st.markdown('- Set the minimum impressions and average position threshold as required.')
st.markdown('- Click on the "Run" button to process the data.')

client_id = st.text_input("Client ID")
client_secret = st.text_input("Client Secret", type="password")

if client_id and client_secret:
    auth_url, flow = get_authorization_url(client_id, client_secret)

    if st.button('Authorize Access'):
        st.markdown(f"[Authorize Access]({auth_url})")

    authorization_response = st.text_input("Enter the authorization code here:")

    if authorization_response:
        credentials = exchange_code_for_credentials(flow, authorization_response)
        searchconsole = build('webmasters', 'v3', credentials=credentials)
        sites = searchconsole.sites().list().execute()

        site_url = st.selectbox('Select your site:', [site['siteUrl'] for site in sites['siteEntry']])
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")

        min_impressions = st.number_input('Enter Minimum Impressions:', min_value=1, value=500)
        position_threshold = st.number_input('Enter Average Position Threshold:', min_value=1, value=20)

        if st.button('Run Analysis'):
            response = searchconsole.searchanalytics().query(
                siteUrl=site_url,
                body={
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d'),
                    'dimensions': ['query', 'page'],
                    'rowLimit': 10000
                }
            ).execute()

            rows = response['rows']
            data = pd.DataFrame([{
                'Query': row['keys'][0],
                'Landing Page': row['keys'][1],
                'Impressions': row['impressions'],
                'Url Clicks': row['clicks'],
                'Average Position': row['position']
            } for row in rows])

            st.markdown('### Data Fetched From Google Search Console')
            st.dataframe(data)

            result_df = find_pages_to_merge(data, position_threshold)

            if not result_df.empty:
                st.markdown('### Pages To Merge')
                st.dataframe(result_df)
                total_pages_to_merge = result_df['Number of Pages to Merge'].sum()
                st.markdown(f'#### Total Number of Pages to Merge: {total_pages_to_merge}')
                csv = result_df.to_csv(index=False).encode()
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name='pages_to_merge.csv',
                    mime='text/csv'
                )
            else:
                st.write('No pages to merge found with the chosen parameters.')
else:
    st.warning('Please enter your Google Cloud Client ID and Client Secret.')
