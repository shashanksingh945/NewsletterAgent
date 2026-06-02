# Autonomous AI Newsletter Agent using Ollama, LangGraph, Tavily, and Streamlit

## Project Overview

This project is an autonomous AI agent that works as a **Newsletter Agent**.

The agent receives a plain English goal:

> Create a weekly newsletter on latest AI agent news and send it to our subscribers.

After receiving the goal, the agent automatically performs research, selects relevant articles, summarizes them, generates a clean newsletter, reviews and improves its own output, and simulates sending by saving the newsletter as an HTML file.

This project uses a local LLM through **Ollama**, which allows unlimited free local testing without depending on paid LLM APIs like Gemini, Grok, Claude, or OpenAI.

---

## Assignment Objective

Build a mini autonomous AI agent that can act as a **Newsletter Agent**.

The agent must autonomously:

* Research the latest AI agent news
* Summarize the top relevant articles
* Generate a clean newsletter in HTML format
* Simulate sending the newsletter
* Use multi-step reasoning
* Show tool usage
* Include self-reflection or critique
* Support Fully Autonomous and Human-in-the-Loop mode
* Run through one function call

---

## Tech Stack

* Python
* LangGraph
* LangChain
* Ollama
* Llama 3.2 local model
* Tavily Search API
* Streamlit
* dotenv

---

## Project Structure

```txt
NewsletterAgent/
│
├── agent.py
├── app.py
├── testOllama.py
├── testTavily.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── outputs/
```

---

## Agent Workflow

```txt
User Goal
   ↓
Planning Node
   ↓
Search Query Node
   ↓
Tavily Research Node
   ↓
Article Selection Node
   ↓
Summarization Node
   ↓
Newsletter Writer Node
   ↓
Self-Critique and Improvement Node
   ↓
Subject Line Node
   ↓
Output Node
   ↓
HTML newsletter saved inside outputs/
```

---

## Features

### 1. Plain English Goal Input

The agent accepts a goal like:

```txt
Create a weekly newsletter on latest AI agent news and send it to our subscribers.
```

### 2. Autonomous Workflow

The full workflow runs using one function:

```python
run_newsletter_agent(goal, mode="auto")
```

### 3. Web Research Tool

The project uses Tavily Search API to fetch latest AI agent news.

### 4. Local LLM

The project uses Ollama with:

```txt
llama3.2:3b
```

This avoids API rate limits from Gemini or Grok.

### 5. Newsletter Generation

The final newsletter is generated in clean HTML format.

### 6. Self-Critique

The agent reviews and improves its own newsletter before final output.

### 7. Simulated Sending

The newsletter is saved as an HTML file inside the `outputs/` folder.

### 8. Human-in-the-Loop Mode

The agent can pause after planning and ask for human approval before continuing.

---

## Fully Autonomous vs Human-in-the-Loop

### Fully Autonomous Mode

In Fully Autonomous mode, the agent completes the whole task by itself:

```txt
Goal → Plan → Research → Summarize → Write → Review → Save Output
```

Use this mode for Streamlit.

### Human-in-the-Loop Mode

In Human-in-the-Loop mode, the agent creates a plan and waits for human approval before continuing.

This mode is best used in the terminal because it uses `input()`.

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/NewsletterAgent.git
cd NewsletterAgent
```

---

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4: Install Ollama

Download and install Ollama from:

```txt
https://ollama.com/download
```

After installation, check:

```bash
ollama --version
```

---

### Step 5: Pull Local Model

```bash
ollama pull llama3.2:3b
```

Test it:

```bash
ollama run llama3.2:3b
```

Then type:

```txt
Say hello
```

Exit using:

```txt
/bye
```

---

### Step 6: Create `.env` File

Create a `.env` file in the project root.

```env
TAVILY_API_KEY=your_tavily_api_key_here
OLLAMA_MODEL=llama3.2:3b
```

Do not upload `.env` to GitHub.

---

## Testing

### Test Ollama

```bash
python testOllama.py
```

Expected output:

```txt
Hello! Nice to meet you.
```

### Test Tavily

```bash
python testTavily.py
```

Expected output:

```txt
<class 'dict'>
```

The response should contain a `results` list.

---

## Run the Agent in Terminal

```bash
python agent.py
```

If successful, it will print:

```txt
Agent completed successfully.
Subject: ...
Output file: outputs/weekly_ai_agent_newsletter_...
```

---

## Run the Streamlit App

```bash
python -m streamlit run app.py
```

Then open:

```txt
http://localhost:8501
```

Use **Fully Autonomous** mode for Streamlit.

---

## Output

The generated newsletter is saved inside:

```txt
outputs/
```

Example:

```txt
outputs/weekly_ai_agent_newsletter_2026_06_02_12_30_45.html
```

---

## Assignment Requirements Covered

| Requirement                | Status |
| -------------------------- | ------ |
| Plain English goal input   | Done   |
| Autonomous agent           | Done   |
| Multi-step reasoning       | Done   |
| Web research               | Done   |
| Top article summarization  | Done   |
| Newsletter generation      | Done   |
| Simulated sending          | Done   |
| Self-reflection / critique | Done   |
| Human-in-the-loop toggle   | Done   |
| One function call          | Done   |
| Simple frontend            | Done   |
| Local LLM using Ollama     | Done   |

---

## Tools Used

### Ollama

Used as the local LLM provider.

Model used:

```txt
llama3.2:3b
```

### Tavily

Used for real-time web search.

### LangGraph

Used to create the multi-step agent workflow.

### Streamlit

Used to create a simple frontend for interacting with the agent.

---

## Important Notes

* Ollama runs locally on your machine.
* Tavily is required only for web research.
* `.env` should never be pushed to GitHub.
* The `outputs/` folder is ignored because generated newsletters should not be committed.
* Streamlit mode should use Fully Autonomous mode.
* Human-in-the-Loop mode is better for terminal execution.

---

## Future Improvements

* Add email sending using SMTP
* Add subscriber database
* Add newsletter scheduling
* Add PDF export
* Add better article ranking
* Add support for multiple newsletter topics
* Add admin dashboard for reviewing newsletters
