from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    temperature=0.4
)

response = llm.invoke("Say hello in one short sentence.")
print(response.content)