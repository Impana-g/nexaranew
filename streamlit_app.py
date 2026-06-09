import streamlit as st
import requests

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Nexara Investment Intelligence",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("📈 Nexara Investment Intelligence")
st.caption("AI-Powered Investment Analysis Platform")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Nexara AI")

st.sidebar.info(
    """
    Features:
    
    • NLP Query Analysis
    
    • Company Detection
    
    • Live Tavily News Search
    
    • Sentiment Analysis
    
    • Risk Assessment
    
    • Investment Recommendations
    """
)

# -----------------------------
# User Input
# -----------------------------
query = st.text_input(
    "Enter your investment query",
    placeholder="Example: Can I invest in IBM?"
)

# -----------------------------
# Analyze Button
# -----------------------------
if st.button("Analyze", type="primary"):

    if not query:
        st.warning("Please enter a query.")
        st.stop()

    with st.spinner("Analyzing investment query..."):

        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analyze",
                json={"query": query},
                timeout=30
            )

            if response.status_code != 200:
                st.error("Failed to connect to API.")
                st.stop()

            result = response.json()

        except Exception as e:
            st.error(f"Connection Error: {e}")
            st.stop()

    # -----------------------------
    # Recommendation
    # -----------------------------
    recommendation = result["final_recommendation"]

    st.subheader("📌 Recommendation")

    if "BUY" in recommendation:
        st.success(recommendation)

    elif "HOLD" in recommendation:
        st.warning(recommendation)

    elif "AVOID" in recommendation:
        st.error(recommendation)

    else:
        st.info(recommendation)

    # -----------------------------
    # Top Metrics
    # -----------------------------
    bg = result["bg_check"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Company",
            bg["ticker"]
        )

    with col2:
        st.metric(
            "Risk Level",
            bg["risk_level"]
        )

    with col3:
        st.metric(
            "Accuracy Score",
            f"{bg['accuracy_score'] * 100:.0f}%"
        )

    # -----------------------------
    # Confidence Score
    # -----------------------------
    confidence = int(result["confidence"] * 100)

    st.subheader("🎯 Confidence Score")

    st.progress(confidence)

    st.write(f"Confidence: {confidence}%")

    # -----------------------------
    # Sentiment
    # -----------------------------
    sentiment = result["sentiment"]

    st.subheader("😊 Sentiment Analysis")

    st.write(
        f"**Label:** {sentiment['label']}"
    )

    st.progress(
        int(sentiment["score"] * 100)
    )

    st.info(
        sentiment["explanation"]
    )

    # -----------------------------
    # Company Summary
    # -----------------------------
    st.subheader("🏢 Company Summary")

    st.write(
        result["kb_snapshot"]["summary"]
    )

    # -----------------------------
    # Latest News
    # -----------------------------
    st.subheader("📰 Latest News")

    seen = set()

    for news in result["kb_snapshot"]["news_headlines"]:
        if news not in seen:
            st.write(f"📰 {news}")
            seen.add(news)

    # -----------------------------
    # Financial Signals
    # -----------------------------
    st.subheader("📊 Financial Signals")

    signals = result["kb_snapshot"]["financial_signals"]

    if signals:
        for signal in signals:
            st.success(signal)
    else:
        st.info("No financial signals available.")

    # -----------------------------
    # Background Check
    # -----------------------------
    st.subheader("🔍 Background Check")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Risk Level",
            bg["risk_level"]
        )

    with col2:
        st.metric(
            "Accuracy",
            f"{bg['accuracy_score'] * 100:.0f}%"
        )

    with col3:
        st.metric(
            "Red Flags",
            len(bg["red_flags"])
        )

# -----------------------------
# PDF Analysis
# -----------------------------
st.divider()

st.header("📄 PDF Investment Analysis")

uploaded_file = st.file_uploader(
    "Upload Annual Report / Financial Report",
    type=["pdf"]
)

if uploaded_file is not None:

    if st.button("Analyze PDF"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file,
                "application/pdf"
            )
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/v1/analyze-pdf",
                files=files,
                timeout=60
            )

            result = response.json()

            st.subheader("📌 Recommendation")

            if result["recommendation"] == "N/A":

                st.info(result["message"])

            else:

                st.success(result["recommendation"])

                st.write("Risk:", result["risk"])

                st.write(
                    "Positive Signals:",
                    result["positive_signals"]
                )

                st.write(
                    "Negative Signals:",
                    result["negative_signals"]
                )

            st.subheader("📄 Document Preview")

            st.text_area(
                "Preview",
                result["preview"],
                height=250
            )

        except Exception as e:
            st.error(f"Error: {e}")

# -----------------------------
# RAG Question Answering
# -----------------------------
# -----------------------------
# RAG Question Answering
# -----------------------------
st.divider()

st.header("💬 Ask Questions About Uploaded PDF")

question = st.text_input(
    "Ask a question about the uploaded document"
)

if st.button("Ask PDF"):

    if not question:
        st.warning("Please enter a question.")

    else:

        try:

            response = requests.post(
                "http://127.0.0.1:8000/api/v1/ask",
                json={
                    "question": question
                },
                timeout=60
            )

            result = response.json()

            st.subheader("🤖 AI Answer")

            if "answer" in result:

                st.success(
                    result["answer"]
                )

            if result.get("answer_chunks"):

                with st.expander("Retrieved Chunks"):

                    for chunk in result["answer_chunks"]:

                        st.write(chunk)

            else:

                st.warning(
                    "No relevant information found."
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )