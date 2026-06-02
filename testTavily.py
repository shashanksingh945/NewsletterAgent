from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

search_tool = TavilySearch(
    max_results=5,
    topic="news",
    include_answer=False,
    include_raw_content=False
)

result = search_tool.invoke({
    "query": "latest AI agent news"
})

print(type(result))
print(result)