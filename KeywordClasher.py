import streamlit as st
import pandas as pd
import numpy as np

# Title of the Streamlit app
st.title('SEO Pages Merger Tool')

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# If a file is uploaded
if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)
    
    # Slider widget for minimum impressions
    min_impressions = st.slider('Choose Minimum Impressions:', 0, 1000, 500)
    
    # Slider widget for average position threshold
    position_threshold = st.slider('Choose Average Position Threshold:', 1, 100, 20)
    
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
    else:
        st.write('No pages to merge found with the chosen parameters.')

else:
    st.write('Please upload a CSV file.')
