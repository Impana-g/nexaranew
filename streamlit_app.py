import streamlit as st
import requests

st.title("Nexara Investment Intelligence")

query = st.text_input("Enter your investment query")

if st.button("Analyze"):
    if query:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze",
            json={"query": query}
        )

        if response.status_code == 200:
            result = response.json()

            st.subheader("Recommendation")
            st.write(result["final_recommendation"])

            st.subheader("Sentiment")
            st.write(result["sentiment"])

            st.subheader("Background Check")
            st.write(result["bg_check"])

            st.subheader("Knowledge Base")
            st.write(result["kb_snapshot"])

        else:
            st.error("API request failed")