import streamlit as st
import pandas as pd
import numpy as np
import base64

# Title of the Streamlit app
st.title('SEO Pages Merger Tool')

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Input for minimum impressions
min_impressions = st.number_input('Enter Minimum Impressions:', min_value=1, value=500)

# Input for average position threshold
position_threshold = st.number_input('Enter Average Position Threshold:', min_value=1, value=20)

# Run button
if st.button('Run'):
    # Check if file is uploaded
    if uploaded_file is not None:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)
        
        # Process the data and apply filters
        filtered_data = data[data['Impressions'] >= min_impressions]
        aggregated_data = filtered_data.groupby(['Query', 'Landing Page']).agg(
            total_clicks=('Url Clicks', 'sum'),
            total_impressions=('Impressions', 'sum'),
            avg_position=('Average Position', 'mean')
        ).reset_index()

        # Find pages to merge
        result = []
        for query in aggregated_data['Query'].unique():
            subset = aggregated_data[aggregated_data['Query'] == query]
            for _, row in subset.iterrows():
                if row['avg_position'] > position_threshold:
                    best_candidate = subset[subset['avg_position'] <= position_threshold].sort_values('avg_position').head(1)
                    if not best_candidate.empty:
                        result.append({
                            'query': row['Query'],
                            'page_to_merge': row['Landing Page'],
                            'merge_into': best_candidate.iloc[0]['Landing Page'],
                            'total_clicks': row['total_clicks'],
                            'total_impressions': row['total_impressions'],
                            'avg_position': row['avg_position']
                        })

        # Display the result
        result_df = pd.DataFrame(result)
        if not result_df.empty:
            st.write(result_df)
            
            # Convert the DataFrame to CSV and create a download button
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
