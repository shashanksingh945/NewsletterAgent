import streamlit as st
from agent import run_newsletter_agent


st.set_page_config(
    page_title="AI Newsletter Agent",
    page_icon="📰",
    layout="wide"
)

st.title("📰 AI Newsletter Agent")

st.write(
    """
    This autonomous agent researches the latest AI agent news, summarizes selected articles,
    generates an HTML newsletter, reviews and improves it, and simulates sending by saving
    the newsletter as an HTML file.
    """
)

with st.sidebar:
    st.header("Agent Settings")

    mode_option = st.radio(
        "Choose Mode",
        ["Fully Autonomous", "Human-in-the-Loop"],
        index=0
    )

    st.info(
        "For Streamlit Cloud deployment, use Fully Autonomous mode. "
        "Human-in-the-Loop mode is better for terminal execution."
    )

goal = st.text_area(
    "Enter newsletter goal",
    value="Create a weekly newsletter on latest AI agent news and send it to our subscribers.",
    height=120
)

run_button = st.button("Run Newsletter Agent", type="primary")

if run_button:
    mode = "auto" if mode_option == "Fully Autonomous" else "human"

    if mode == "human":
        st.warning(
            "Human-in-the-Loop uses terminal input in this version. "
            "Please use Fully Autonomous mode on Streamlit Cloud."
        )
        st.stop()

    with st.spinner("Agent is planning, researching, writing, and reviewing the newsletter..."):
        try:
            result = run_newsletter_agent(goal, mode=mode)
        except Exception as e:
            st.error(f"Agent crashed: {str(e)}")
            st.stop()

    if result.get("error"):
        st.error(result["error"])
    else:
        st.success("Newsletter generated successfully!")

        st.subheader("1. Agent Plan")
        st.write(result["plan"])

        st.subheader("2. Search Query")
        st.code(result["search_query"])

        st.subheader("3. Selected Articles")
        for index, article in enumerate(result["selected_articles"], start=1):
            st.markdown(f"### {index}. {article['title']}")
            st.write(article["url"])

            if article.get("published_date"):
                st.caption(f"Published: {article['published_date']}")

        st.subheader("4. Summaries")
        st.write(result["summaries"])

        st.subheader("5. Self-Critique")
        st.write(result["critique"])

        st.subheader("6. Subject Line")
        st.code(result["subject_line"])

        st.subheader("7. Newsletter Preview")
        st.components.v1.html(
            result["final_newsletter"],
            height=900,
            scrolling=True
        )

        st.subheader("8. HTML Code")
        st.code(result["final_newsletter"], language="html")

        st.download_button(
            label="Download Newsletter HTML",
            data=result["final_newsletter"],
            file_name="weekly_ai_agent_newsletter.html",
            mime="text/html"
        )

        st.info(f"Simulated output saved at runtime path: {result['output_file']}")