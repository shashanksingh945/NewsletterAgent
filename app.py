import streamlit as st
from agent import run_newsletter_agent


st.set_page_config(
    page_title="Local AI Newsletter Agent",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Local AI Newsletter Agent using Ollama")

st.write("""
         This agent uses a local Ollama model for reasoning and writing, Tavily for live news search,
        LangGraph for workflow orchestration, and Streamlit for the frontend.
        """
)

goal = st.text_area(
    "Enter your newsletter goal",
    value="Create a weekly newsletter on latest AI agent news and send it to our subscribers.",
    height=120
)

mode_option = st.radio(
    "Choose Mode",
    ["Fully Autonomous", "Human-in-the-Loop"]
)

if st.button("Run Newsletter Agent"):
    mode = "auto" if mode_option == "Fully Autonomous" else "human"

    with st.spinner("Running local AI agent..."):
        result = run_newsletter_agent(goal, mode=mode)

    if result.get("error"):
        st.error(result["error"])
    else:
        st.success("Newsletter generated successfully!")

        st.subheader("Agent Plan")
        st.write(result["plan"])

        st.subheader("Search Query")
        st.code(result["search_query"])

        st.subheader("Selected Articles")
        for index, article in enumerate(result["selected_articles"], start=1):
            st.markdown(f"### {index}. {article['title']}")
            st.write(article["url"])
            st.caption(article.get("published_date", ""))

        st.subheader("Summaries")
        st.write(result["summaries"])

        st.subheader("Self-Review")
        st.write(result["critique"])

        st.subheader("Subject Line")
        st.code(result["subject_line"])

        st.subheader("Newsletter Preview")
        st.components.v1.html(
            result["final_newsletter"],
            height=900,
            scrolling=True
        )

        st.subheader("HTML Code")
        st.code(result["final_newsletter"], language="html")

        st.download_button(
            label="Download Newsletter HTML",
            data=result["final_newsletter"],
            file_name="weekly_ai_agent_newsletter.html",
            mime="text/html"
        )

        st.info(f"Saved locally at: {result['output_file']}")