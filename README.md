# Autonomous AI Newsletter Agent using Groq, LangGraph, Tavily, and Streamlit

## Project Overview

This project is an autonomous AI agent that works as a **Newsletter Agent**.

The agent receives a plain English goal:

> Create a weekly newsletter on latest AI agent news and send it to our subscribers.

After receiving the goal, the agent automatically plans the task, researches the latest AI agent news, selects relevant articles, summarizes them, generates a clean HTML newsletter, reviews and improves its own output, and simulates sending by saving the newsletter as an HTML file.

This version is designed to be **deployable on Streamlit Cloud**. It uses **Groq API** as the cloud LLM provider instead of Ollama because Streamlit Cloud cannot run local Ollama models.

---

## Live Demo

Streamlit App Link:

```txt
https://newsletteragent-ybfijai8jmnaledfdfibew.streamlit.app/
```

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
* Streamlit
* LangGraph
* LangChain
* Groq API
* Tavily Search API
* dotenv

---

## Why Groq is Used

Initially, the project was tested with local Ollama and other LLM APIs. However, for Streamlit Cloud deployment, a cloud-based LLM is required.

Ollama works locally because it runs on the user's machine, but Streamlit Cloud cannot access a local Ollama server. Therefore, this deployable version uses **Groq API** for LLM tasks such as planning, summarization, newsletter generation, critique, and improvement.

---

## Project Structure

```txt
NewsletterAgent/
│
├── agent.py
├── app.py
├── testGroq.py
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
HTML Newsletter Saved
```

---

## Main Features

### 1. Plain English Goal Input

The agent accepts a goal such as:

```txt
Create a weekly newsletter on latest AI agent news and send it to our subscribers.
```

---

### 2. Fully Autonomous Workflow

The complete workflow can be triggered using one function:

```python
run_newsletter_agent(goal, mode="auto")
```

---

### 3. Web Research Tool

The project uses **Tavily Search API** to fetch the latest AI agent news from the web.

---

### 4. Cloud LLM using Groq

The project uses Groq API for:

* Planning
* Article summarization
* Newsletter generation
* Self-review
* Newsletter improvement
* Subject line generation

---

### 5. Article Selection

The agent selects the most relevant articles based on Tavily search scores.

---

### 6. Newsletter Generation

The final newsletter is generated in clean HTML format.

---

### 7. Self-Critique and Improvement

The agent reviews the newsletter and improves it before final output.

---

### 8. Simulated Sending

The project simulates sending by saving the final newsletter as an HTML file inside the `outputs/` folder.

---

### 9. Streamlit Frontend

A simple Streamlit interface is provided to interact with the agent.

---

## Fully Autonomous vs Human-in-the-Loop

### Fully Autonomous Mode

In Fully Autonomous mode, the agent runs the entire process without asking for approval.

```txt
Goal → Plan → Research → Summarize → Write → Review → Save
```

This mode is recommended for Streamlit Cloud deployment.

---

### Human-in-the-Loop Mode

In Human-in-the-Loop mode, the agent creates a plan and waits for human approval before continuing.

This mode is better for terminal execution because it uses terminal input.

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
| Streamlit deployable       | Done   |

---

## Tools Used

### Groq API

Used as the LLM provider for planning, summarization, newsletter writing, critique, improvement, and subject line generation.

### Tavily Search API

Used for latest AI agent news research.

### LangGraph

Used to create the multi-step autonomous agent workflow.

### Streamlit

Used to create the frontend interface and deploy the project online.

---

## Future Improvements

* Add real email sending using SMTP
* Add subscriber database
* Add scheduled weekly newsletter generation
* Add PDF export
* Add better article ranking
* Add support for multiple newsletter topics
* Add admin review dashboard
* Add analytics for newsletter performance


