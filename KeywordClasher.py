import streamlit as st
import pandas as pd
import numpy as np
import base64

def merge_pages(data, min_impressions, position_threshold):
    # Filter out rows with impressions below the minimum threshold
    filtered_data = data[data['Impressions'] >= min_impressions]
    
    # Group by query and landing_page
    grouped_data = filtered_data.groupby(['Query', 'Landing Page']).agg({
        'Url Clicks': 'sum',
        'Impressions': 'sum',
        'Average Position': 'mean'
    }).reset_index()

    # Determine pages to merge
    pages_to_merge = []
    for query in grouped_data['Query'].unique():
        subset = grouped_data[grouped_data['Query'] == query]
        best_candidates = subset[(subset['Average Position'] <= position_threshold)]
        for _, row in subset.iterrows():
            if row['Average Position'] > position_threshold:
                merge_into = best_candidates.sort_values('Average Position').head(1)
                if not merge_into.empty:
                    pages_to_merge.append({
                        'query': row['Query'],
                        'page_to_merge': row['Landing Page'],
                        'merge_into': merge_into.iloc[0]['Landing Page'],
                        'page_to_merge_clicks': row['Url Clicks'],
                        'page_to_merge_impressions': row['Impressions'],
                        'page_to_merge_avg_position': row['Average Position']
                    })

    # Create a DataFrame from the results
    result_df = pd.DataFrame(pages_to_merge)
    return result_df


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
        result_df = merge_pages(data, min_impressions, position_threshold)

        # Display the result
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
