import os
import time
from typing import TypedDict, List, Dict, Optional
from datetime import datetime

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_tavily import TavilySearch


load_dotenv()


#-------------------------------------1. Agent State-----------------------------------------------------


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

#-------------------------------------2. Ollama Local LLM Setup-----------------------------------------------------


def get_ollama_llm():
    """
    Creates local Ollama LLM client.
    Make sure Ollama is running and the model is pulled.
    """

    model_name = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    llm = ChatOllama(
        model=model_name,
        temperature=0.4
    )

    return llm


llm = get_ollama_llm()

#-------------------------------------3. Tavily Search Tool-----------------------------------------------------

def get_search_tool():
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY is missing. Add it to your .env file.")

    search_tool = TavilySearch(
        max_results=10,
        topic="news",
        include_answer=False,
        include_raw_content=False
    )

    return search_tool


search_tool = get_search_tool()

#-------------------------------------4. Helper LLM Function-----------------------------------------------------

def call_llm(prompt: str, retries: int = 2) -> str:
    """
    Calls local Ollama model.
    Retry is added in case local Ollama server is temporarily unavailable.
    """

    for attempt in range(retries):
        try:
            response = llm.invoke(prompt)
            return response.content

        except Exception as e:
            error_message = str(e)

            if "connection" in error_message.lower() or "refused" in error_message.lower():
                wait_time = 3 * (attempt + 1)
                print(f"Ollama connection issue. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e

    raise RuntimeError(
        "Ollama failed. Make sure Ollama is installed and running. "
        "Also run: ollama pull llama3.2:3b"
    )


def clean_html_output(text: str) -> str:
    """
    Removes extra chatbot-style text before/after HTML.
    """

    text = text.strip()

    # Remove markdown code fences if model adds them
    text = text.replace("```html", "").replace("```", "").strip()

    # Find where actual HTML starts
    html_start_positions = [
        text.find("<!DOCTYPE"),
        text.find("<html"),
        text.find("<body"),
        text.find("<div")
    ]

    valid_positions = [pos for pos in html_start_positions if pos != -1]

    if valid_positions:
        start = min(valid_positions)
        text = text[start:]

    return text.strip()
#-------------------------------------5. Graph Nodes-----------------------------------------------------

def planning_node(state: NewsletterState) -> NewsletterState:
    """
    Step 1: Agent creates a plan.
    """

    prompt = f"""
    You are an autonomous AI Newsletter Agent.

    Goal:
    {state["goal"]}

    Create a short practical execution plan with these steps:
    1. Research latest AI agent news
    2. Select top articles
    3. Summarize articles
    4. Generate newsletter
    5. Review and improve
    6. Simulate sending

    Keep it concise.
    """

    state["plan"] = call_llm(prompt)
    return state

def human_review_node(state: NewsletterState) -> NewsletterState:
    """
    Human-in-the-loop checkpoint.
    Used only when mode='human'.
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
    Step 2: Creates a stable search query.
    No LLM call here to save time.
    """

    state["search_query"] = (
        "latest AI agent news autonomous AI agents LLM agents agentic AI "
        "OpenAI Google Anthropic LangGraph AutoGen CrewAI"
    )

    return state


def research_node(state: NewsletterState) -> NewsletterState:
    """
    Step 3: Uses Tavily web search.
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
    Step 4: Selects top 5 articles using Tavily score.
    No LLM call here, so it is faster and free.
    """

    if not state["raw_articles"]:
        state["error"] = "No articles found during research."
        return state

    sorted_articles = sorted(
        state["raw_articles"],
        key=lambda article: article.get("score", 0),
        reverse=True
    )

    state["selected_articles"] = sorted_articles[:5]

    return state


def summarize_articles_node(state: NewsletterState) -> NewsletterState:
    """
    Step 5: Summarizes all selected articles in one local LLM call.
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

            Keep it clear and professional.

            Articles:
            {articles_text}
            """

    state["summaries"] = call_llm(prompt)
    return state


def newsletter_writer_node(state: NewsletterState) -> NewsletterState:
    """
    Step 6: Generates HTML newsletter.
    """

    prompt = f"""
    Create a clean HTML email newsletter.

    Topic:
    Latest AI Agent News

    Goal:
    {state["goal"]}

    Use this structure:
    - Header
    - Short introduction
    - 5 news sections
    - Each section should include title, summary, why it matters, key takeaway, source link
    - Closing note

    Rules:
    - Use simple inline CSS
    - Do not use JavaScript
    - Keep it professional
    - Return only valid HTML

    Article summaries:
    {state["summaries"]}
    """

    raw_html = call_llm(prompt)
    state["newsletter_draft"] = clean_html_output(raw_html)
    return state


def critique_node(state: NewsletterState) -> NewsletterState:
    """
    Step 7: Self-review and improvement in one local LLM call.
    """

    prompt = f"""
    You are an HTML email generator.

    Your task:
    Review and improve the newsletter below.

    Very important rules:
    - Output ONLY raw HTML.
    - Do NOT write explanations.
    - Do NOT write "Here is the improved final HTML newsletter".
    - Do NOT use markdown.
    - Do NOT wrap the answer in ```html.
    - The first character of your response must be <
    - The last part of your response must be valid HTML.

    Newsletter:
    {state["newsletter_draft"]}
    """

    state["critique"] = "Newsletter reviewed and improved by the local Ollama model."
    raw_html = call_llm(prompt)
    state["final_newsletter"] = clean_html_output(raw_html)

    return state


def subject_line_node(state: NewsletterState) -> NewsletterState:
    """
    Step 8: Creates email subject line.
    """

    prompt = f"""
        Create one short professional subject line for this AI agent newsletter.

        Return only the subject line.

        Newsletter:
        {state["final_newsletter"][:1500]}
        """

    subject = call_llm(prompt)
    state["subject_line"] = subject.strip().replace('"', "")

    return state


def output_node(state: NewsletterState) -> NewsletterState:
    """
    Step 9: Simulates sending by saving HTML file.
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

#-------------------------------------6. Conditional Routing-----------------------------------------------------


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


#-------------------------------------7. Build LangGraph-----------------------------------------------------

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

#-------------------------------------8. One Function Agent Runner-----------------------------------------------------

def run_newsletter_agent(goal: str, mode: str = "auto") -> NewsletterState:
    """
    One function call to run the full agent.

    mode:
    - "auto"  = fully autonomous
    - "human" = human-in-the-loop after planning
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



#-------------------------------------9. Terminal Run-----------------------------------------------------

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