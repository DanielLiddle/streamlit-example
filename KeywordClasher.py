import streamlit as st
import pandas as pd
import base64


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


st.title('SEO Pages Merger Tool')

st.markdown('## Instructions')
st.markdown('- Upload a CSV file containing your SEO data with the columns: Query, Landing Page, Impressions, Url Clicks, Average Position')
st.markdown('- Set the minimum impressions and average position threshold as required.')
st.markdown('- Click on the "Run" button to process the data.')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

min_impressions = st.number_input('Enter Minimum Impressions:', min_value=1, value=500)

position_threshold = st.number_input('Enter Average Position Threshold:', min_value=1, value=20)

if st.button('Run'):
    if uploaded_file is not None:
        st.markdown('### Uploaded Data')
        data = pd.read_csv(uploaded_file)
        st.dataframe(data)
        
        filtered_data = data[data['Impressions'] >= min_impressions]

        grouped_data = filtered_data.groupby(['Query', 'Landing Page']).agg({'Impressions': 'sum', 'Url Clicks': 'sum', 'Average Position': 'mean'}).reset_index()

        result_df = find_pages_to_merge(grouped_data, position_threshold)

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
        st.warning('Please upload a CSV file.')
