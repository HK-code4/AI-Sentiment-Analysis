import streamlit as st
import requests
import pandas as pd
import os

# File path to store fetched reviews
file_path = "fetched_reviews.csv"

# Load previously saved reviews from CSV if it exists
if os.path.exists(file_path):
    st.session_state.fetched_reviews = pd.read_csv(file_path).to_dict(orient="records")
else:
    st.session_state.fetched_reviews = []

# Streamlit app
st.title("AI-Powered Product Review Sentiment Analyzer")
st.write("Enter a product review for analysis")

# Input box for user to enter review text and product ID
product_id = st.text_input("Product ID:")
review_text = st.text_area("Product Review:")


# Function to display reviews and sentiment stats
def display_reviews_and_stats():
    if st.session_state.fetched_reviews:
        # Display previously fetched reviews
        st.write("### Previously Fetched Reviews:")
        fetched_df = pd.DataFrame(st.session_state.fetched_reviews)
        st.dataframe(fetched_df)

        # Calculate sentiment statistics
        positive_reviews = fetched_df[fetched_df['Sentiment'] == 'POSITIVE']
        negative_reviews = fetched_df[fetched_df['Sentiment'] == 'NEGATIVE']

        total_reviews = len(fetched_df)
        positive_percentage = (len(positive_reviews) / total_reviews) * 100 if total_reviews > 0 else 0
        negative_percentage = (len(negative_reviews) / total_reviews) * 100 if total_reviews > 0 else 0

        # Display sentiment statistics as a rating
        st.write("### Sentiment Rating Statistics")
        st.write(f"Positive Reviews: {positive_percentage:.2f}%")
        st.write(f"Negative Reviews: {negative_percentage:.2f}%")


# Analyze button
if st.button("Analyze"):
    response = requests.post("http://127.0.0.1:8000/analyze/", json={"review": review_text})

    if response.status_code == 200:
        result = response.json()
        # Extract sentiment and confidence using get to avoid KeyError
        sentiment = result.get("sentiment", "N/A")
        confidence = result.get("score", "N/A")

        st.write("Sentiment:", sentiment)
        st.write("Confidence Score:", confidence)

        # Create DataFrame with correctly formatted data
        new_review_data = {
            "Product ID": product_id,
            "Review": review_text,
            "Sentiment": sentiment,
            "Confidence": confidence
        }

        # Append new review to the session state for displaying and save to CSV
        st.session_state.fetched_reviews.append(new_review_data)

        # Save updated reviews to CSV
        pd.DataFrame(st.session_state.fetched_reviews).to_csv(file_path, index=False)

        st.write("### New Review Data:")
        st.dataframe(pd.DataFrame([new_review_data]))  # Show the newly analyzed review

    else:
        st.write("Error:", response.json().get("detail", "An error occurred"))

# Fetching and analyzing reviews from Google Sheets
google_sheets_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhXNtaZ31_bOvD1UmVhZH9C2IZyqby2BIL9vL8cNLH_0N3otnTuNXQjoeorLfUOByMxxtUUVVOByus/pubhtml"

if st.button("Fetch and Analyze Reviews from Google Sheets"):
    try:
        # Call the FastAPI endpoint to fetch reviews
        response = requests.post("http://127.0.0.1:8000/fetch_and_analyze/", json={"url": google_sheets_url})

        if response.status_code == 200:
            analysis_result = response.json()
            # Extend fetched reviews and save to CSV
            st.session_state.fetched_reviews.extend(analysis_result["results"])
            pd.DataFrame(st.session_state.fetched_reviews).to_csv(file_path, index=False)

            st.write("Fetched and Analyzed Reviews:")
            st.dataframe(pd.DataFrame(analysis_result["results"]))
        else:
            st.write("Error fetching reviews:", response.json().get("detail", "An error occurred"))
    except Exception as e:
        st.write("An error occurred while fetching reviews:", str(e))

# Display previously fetched reviews and sentiment statistics
display_reviews_and_stats()
