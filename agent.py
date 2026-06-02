import os
import time
from typing import TypedDict, List, Dict, Optional
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


load_dotenv()


# -----------------------------
# 1. Config helpers
# -----------------------------

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Works locally with .env and on Streamlit Cloud with st.secrets.
    """
    value = os.getenv(key)

    if value:
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return default


# -----------------------------
# 2. Agent State
# -----------------------------

class NewsletterState(TypedDict):
    goal: str
    mode: str

    plan: str
    search_query: str

    raw_articles: List[Dict]
    selected_articles: List[Dict]
    summaries: str

    newsletter_draft: str
    critique: str
    final_newsletter: str

    subject_line: str
    output_file: str

    error: Optional[str]


# -----------------------------
# 3. Groq LLM Setup
# -----------------------------

def get_groq_llm():
    """
    Creates Groq cloud LLM client.
    This works on Streamlit Cloud.
    """

    groq_api_key = get_secret("GROQ_API_KEY")
    groq_model = get_secret("GROQ_MODEL", "llama-3.1-8b-instant")

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to .env locally or Streamlit secrets in deployment."
        )

    llm = ChatGroq(
        api_key=groq_api_key,
        model=groq_model,
        temperature=0.4,
        max_tokens=1400
    )

    return llm


llm = get_groq_llm()


# -----------------------------
# 4. Tavily Search Tool
# -----------------------------

def get_search_tool():
    tavily_api_key = get_secret("TAVILY_API_KEY")

    if not tavily_api_key:
        raise ValueError(
            "TAVILY_API_KEY is missing. Add it to .env locally or Streamlit secrets in deployment."
        )

    search_tool = TavilySearch(
        tavily_api_key=tavily_api_key,
        max_results=8,
        topic="news",
        include_answer=False,
        include_raw_content=False
    )

    return search_tool


search_tool = get_search_tool()


# -----------------------------
# 5. Helper Functions
# -----------------------------

def call_llm(prompt: str, retries: int = 3) -> str:
    """
    Calls Groq LLM with simple retry handling.
    """

    for attempt in range(retries):
        try:
            response = llm.invoke(prompt)
            return response.content

        except Exception as e:
            message = str(e)

            if "rate" in message.lower() or "timeout" in message.lower() or "temporarily" in message.lower():
                wait_time = 5 * (attempt + 1)
                print(f"LLM temporarily unavailable or rate-limited. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e

    raise RuntimeError("LLM failed after multiple retry attempts.")


def clean_html_output(text: str) -> str:
    """
    Removes extra chatbot-style text and markdown fences before saving HTML.
    """

    text = text.strip()
    text = text.replace("```html", "").replace("```", "").strip()

    possible_starts = [
        text.find("<!DOCTYPE"),
        text.find("<html"),
        text.find("<body"),
        text.find("<div")
    ]

    valid_starts = [pos for pos in possible_starts if pos != -1]

    if valid_starts:
        text = text[min(valid_starts):]

    return text.strip()


# -----------------------------
# 6. Graph Nodes
# -----------------------------

def planning_node(state: NewsletterState) -> NewsletterState:
    prompt = f"""
You are an autonomous AI Newsletter Agent.

Goal:
{state["goal"]}

Create a short execution plan.

Include:
1. Research strategy
2. Article selection
3. Summarization
4. HTML newsletter generation
5. Self-review
6. Simulated sending

Keep it concise and professional.
"""

    state["plan"] = call_llm(prompt)
    return state


def human_review_node(state: NewsletterState) -> NewsletterState:
    """
    Human-in-the-loop is supported for terminal.
    For Streamlit deployment, use Fully Autonomous mode.
    """

    print("\n==============================")
    print("HUMAN REVIEW REQUIRED")
    print("==============================")
    print("\nAgent Plan:\n")
    print(state["plan"])

    approval = input("\nApprove this plan? Type 'yes' to continue: ")

    if approval.strip().lower() != "yes":
        state["error"] = "Human reviewer stopped the agent after planning."
        return state

    return state


def search_query_node(state: NewsletterState) -> NewsletterState:
    """
    Stable search query to avoid unnecessary LLM calls.
    """

    state["search_query"] = (
        "latest AI agent news autonomous AI agents LLM agents agentic AI "
        "OpenAI Google Anthropic LangGraph AutoGen CrewAI"
    )

    return state


def research_node(state: NewsletterState) -> NewsletterState:
    """
    Uses Tavily to search latest AI agent news.
    """

    query = state["search_query"]

    try:
        results = search_tool.invoke({
            "query": query
        })

        articles = []

        if isinstance(results, dict):
            search_results = results.get("results", [])
        elif isinstance(results, list):
            search_results = results
        else:
            search_results = []

        for item in search_results:
            if not isinstance(item, dict):
                continue

            article = {
                "title": item.get("title", "Untitled"),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "published_date": item.get("published_date", ""),
                "score": item.get("score", 0)
            }

            if article["title"] and article["url"] and article["content"]:
                articles.append(article)

        if not articles:
            state["error"] = "No articles found during research."
            state["raw_articles"] = []
            return state

        state["raw_articles"] = articles

    except Exception as e:
        state["error"] = f"Research failed: {str(e)}"
        state["raw_articles"] = []

    return state


def select_articles_node(state: NewsletterState) -> NewsletterState:
    """
    Select top 3 articles using Tavily relevance score.
    """

    if not state["raw_articles"]:
        state["error"] = "No articles found during research."
        return state

    sorted_articles = sorted(
        state["raw_articles"],
        key=lambda article: article.get("score", 0),
        reverse=True
    )

    state["selected_articles"] = sorted_articles[:3]
    return state


def summarize_articles_node(state: NewsletterState) -> NewsletterState:
    """
    Summarizes all selected articles in one LLM call.
    """

    articles_text = ""

    for index, article in enumerate(state["selected_articles"], start=1):
        articles_text += f"""
Article {index}
Title: {article["title"]}
URL: {article["url"]}
Published Date: {article.get("published_date", "")}
Content: {article["content"]}
"""

    prompt = f"""
You are preparing a weekly newsletter about AI agents.

Summarize the following articles.

For each article, write:
- Title
- 2 sentence summary
- Why it matters
- Key takeaway
- Source URL

Keep the language simple, professional, and newsletter-friendly.

Articles:
{articles_text}
"""

    state["summaries"] = call_llm(prompt)
    return state


def newsletter_writer_node(state: NewsletterState) -> NewsletterState:
    """
    Generates clean HTML newsletter.
    """

    prompt = f"""
You are an HTML email newsletter generator.

Create a clean HTML email newsletter.

Topic:
Latest AI Agent News

Goal:
{state["goal"]}

Use this structure:
- Header
- Short intro
- 3 news sections
- Each section must include title, summary, why it matters, key takeaway, source link
- Closing note

Rules:
- Output ONLY raw HTML.
- Do NOT write explanations.
- Do NOT write markdown.
- Do NOT wrap in ```html.
- First character must be <.
- Use simple inline CSS.
- Do not use JavaScript.

Article summaries:
{state["summaries"]}
"""

    raw_html = call_llm(prompt)
    state["newsletter_draft"] = clean_html_output(raw_html)

    return state


def critique_node(state: NewsletterState) -> NewsletterState:
    """
    Self-critique and improvement in one step.
    """

    prompt = f"""
You are an HTML email quality reviewer and editor.

Review and improve the newsletter below.

Check:
1. Relevance to AI agents
2. Clarity
3. Professional tone
4. Source links
5. HTML readability

Very important:
- Output ONLY the improved raw HTML.
- Do NOT write "Here is the improved final HTML newsletter".
- Do NOT write explanations.
- Do NOT use markdown.
- Do NOT wrap in ```html.
- First character must be <.

Newsletter:
{state["newsletter_draft"]}
"""

    state["critique"] = "Newsletter reviewed and improved by the agent."

    raw_html = call_llm(prompt)
    state["final_newsletter"] = clean_html_output(raw_html)

    return state


def subject_line_node(state: NewsletterState) -> NewsletterState:
    prompt = f"""
Create one short professional email subject line for this AI agent newsletter.

Rules:
- Return only the subject line.
- Do not use quotes.
- Maximum 12 words.

Newsletter:
{state["final_newsletter"][:1500]}
"""

    subject = call_llm(prompt)
    state["subject_line"] = subject.strip().replace('"', "")

    return state


def output_node(state: NewsletterState) -> NewsletterState:
    """
    Simulates sending by saving HTML file.
    On Streamlit Cloud, writing to local temporary filesystem is allowed during runtime.
    """

    os.makedirs("outputs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"outputs/weekly_ai_agent_newsletter_{timestamp}.html"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(state["final_newsletter"])

    state["output_file"] = filename

    print("\n==============================")
    print("SIMULATED NEWSLETTER EMAIL")
    print("==============================")
    print(f"Subject: {state['subject_line']}")
    print(f"Saved HTML File: {filename}")
    print("==============================\n")

    return state


# -----------------------------
# 7. Conditional Routing
# -----------------------------

def route_after_planning(state: NewsletterState) -> str:
    if state["mode"] == "human":
        return "human_review"

    return "search_query"


def route_after_human_review(state: NewsletterState) -> str:
    if state.get("error"):
        return "end"

    return "search_query"


def route_after_research(state: NewsletterState) -> str:
    if state.get("error"):
        return "end"

    return "select_articles"


def route_after_selection(state: NewsletterState) -> str:
    if state.get("error"):
        return "end"

    return "summarize_articles"


# -----------------------------
# 8. Build LangGraph
# -----------------------------

def build_newsletter_graph():
    graph = StateGraph(NewsletterState)

    graph.add_node("planning", planning_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("search_query", search_query_node)
    graph.add_node("research", research_node)
    graph.add_node("select_articles", select_articles_node)
    graph.add_node("summarize_articles", summarize_articles_node)
    graph.add_node("newsletter_writer", newsletter_writer_node)
    graph.add_node("critique", critique_node)
    graph.add_node("subject_line", subject_line_node)
    graph.add_node("output", output_node)

    graph.set_entry_point("planning")

    graph.add_conditional_edges(
        "planning",
        route_after_planning,
        {
            "human_review": "human_review",
            "search_query": "search_query"
        }
    )

    graph.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "search_query": "search_query",
            "end": END
        }
    )

    graph.add_edge("search_query", "research")

    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "select_articles": "select_articles",
            "end": END
        }
    )

    graph.add_conditional_edges(
        "select_articles",
        route_after_selection,
        {
            "summarize_articles": "summarize_articles",
            "end": END
        }
    )

    graph.add_edge("summarize_articles", "newsletter_writer")
    graph.add_edge("newsletter_writer", "critique")
    graph.add_edge("critique", "subject_line")
    graph.add_edge("subject_line", "output")
    graph.add_edge("output", END)

    return graph.compile()


# -----------------------------
# 9. Runner
# -----------------------------

def run_newsletter_agent(goal: str, mode: str = "auto") -> NewsletterState:
    """
    One function call to run the full agent.

    mode:
    - auto: fully autonomous
    - human: terminal-only human-in-the-loop
    """

    if mode not in ["auto", "human"]:
        raise ValueError("mode must be either 'auto' or 'human'.")

    app = build_newsletter_graph()

    initial_state: NewsletterState = {
        "goal": goal,
        "mode": mode,

        "plan": "",
        "search_query": "",

        "raw_articles": [],
        "selected_articles": [],
        "summaries": "",

        "newsletter_draft": "",
        "critique": "",
        "final_newsletter": "",

        "subject_line": "",
        "output_file": "",

        "error": None
    }

    final_state = app.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    user_goal = "Create a weekly newsletter on latest AI agent news and send it to our subscribers."

    result = run_newsletter_agent(
        goal=user_goal,
        mode="auto"
    )

    if result.get("error"):
        print("Agent failed:", result["error"])
    else:
        print("\nAgent completed successfully.")
        print("Subject:", result["subject_line"])
        print("Output file:", result["output_file"])