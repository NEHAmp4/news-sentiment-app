import streamlit as st
import requests
import pickle
import re
import os

st.title("News Sentiment Analysis App")
st.write("Select a company to view its news sentiment analysis and summaries.")

# Define API base URL (for FastAPI)
API_URL = "https://news.google.com/?hl=en-IN&gl=IN&ceid=IN%3Aen"
# Load list of companies for dropdown
companies = []
placeholder = "-- Select Company --"
try:
    resp = requests.get(f"{API_URL}/companies")
    if resp.status_code == 200:
        companies = resp.json().get("companies", [])
except Exception as e:
    # If API is not available, fall back to local CSV
    try:
        import pandas as pd
        df = pd.read_csv("data/company_list.csv")
        companies = df['Company'].dropna().tolist()
    except Exception as e:
        st.error("Failed to load company list.")
        companies = []
if companies:
    companies = [placeholder] + companies

selected_company = st.selectbox("Company:", companies, index=0)

if selected_company and selected_company != placeholder:
    # Fetch sentiment report data for the selected company
    data = None
    try:
        resp = requests.get(f"{API_URL}/report/{selected_company}")
        if resp.status_code == 200:
            data = resp.json()
    except Exception as e:
        data = None
    # Fallback: if API call failed, try loading local pickle file
    if data is None:
        filename_base = re.sub(r'\W+', '_', selected_company.lower())
        file_path = os.path.join('data', 'output', f"{filename_base}.pkl")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
    if data is None:
        st.error("No data available for the selected company.")
    else:
        st.subheader(f"Sentiment Report for {selected_company}")
        # Display article summaries and sentiments
        st.markdown("### Articles and Summaries")
        for idx, article in enumerate(data.get("Articles", []), start=1):
            st.markdown(f"**{idx}. {article['Title']}**")
            st.write(article.get("Summary", ""))
            st.write(f"Sentiment: {article.get('Sentiment', 'N/A')}")
            topics = article.get("Topics", [])
            if topics:
                st.write("Topics: " + ", ".join(topics))
            st.write("---")
        # Display comparative sentiment analysis
        comp = data.get("Comparative Sentiment Score", {})
        if comp:
            st.markdown("### Comparative Sentiment Analysis")
            # Sentiment Distribution
            dist = comp.get("Sentiment Distribution", {})
            if dist:
                st.write("**Sentiment Distribution:**")
                try:
                    import pandas as pd
                    dist_df = pd.DataFrame(list(dist.items()), columns=["Sentiment", "Count"]).set_index("Sentiment")
                    st.bar_chart(dist_df)  # bar chart visualization
                    st.write(dist_df)      # display counts in a table
                except Exception as e:
                    st.write(dist)
            # Coverage Differences
            differences = comp.get("Coverage Differences", [])
            if differences:
                st.write("**Coverage Differences:**")
                for diff in differences:
                    st.write(f"- **Comparison:** {diff.get('Comparison', '')}")
                    st.write(f"  **Impact:** {diff.get('Impact', '')}")
            # Topic Overlap
            overlap = comp.get("Topic Overlap", {})
            if overlap:
                st.write("**Topic Overlap:**")
                common = overlap.get("Common Topics", [])
                unique_map = {k: v for k, v in overlap.items() if k.startswith("Unique Topics")}
                if common:
                    st.write("Common Topics: " + ", ".join(common))
                for label, topics in unique_map.items():
                    if topics:
                        st.write(f"{label}: " + ", ".join(topics))
                    else:
                        st.write(f"{label}: None")
        # Display overall sentiment analysis text
        final_sent = data.get("Final Sentiment Analysis", "")
        if final_sent:
            st.markdown("### Overall Sentiment")
            st.write(final_sent)
        # Hindi TTS audio for overall sentiment
        if final_sent:
            st.markdown("### Hindi Audio of Overall Sentiment")
            if st.button("Play Audio"):
                from utils.text_to_speech import text_to_speech_hindi
                filename_base = re.sub(r'\W+', '_', selected_company.lower())
                audio_file_path = os.path.join('data', 'output', f"{filename_base}_overall_sentiment_hi.mp3")
                # Generate audio if not already generated
                if not os.path.exists(audio_file_path):
                    text_to_speech_hindi(final_sent, audio_file_path)
                if os.path.exists(audio_file_path):
                    audio_file = open(audio_file_path, 'rb')
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3')
                else:
                    st.error("Audio generation failed.")
