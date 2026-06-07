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

    if bg["positive_signals"]:
        st.write("### Positive Signals")

        for signal in bg["positive_signals"]:
            st.success(signal)

    if bg["red_flags"]:
        st.write("### Red Flags")

        for flag in bg["red_flags"]:
            st.error(flag)

    # -----------------------------
    # Pipeline Stages
    # -----------------------------
    st.subheader("⚙ Analysis Pipeline")

    for stage in result["pipeline_stages"]:
        st.success(stage)