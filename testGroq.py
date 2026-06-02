from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    temperature=0.3
)

response = llm.invoke("Say hello in one short sentence.")
print(response.content)