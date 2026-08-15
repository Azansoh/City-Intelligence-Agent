# 🏙️ City Intelligence AI Agent

An interactive terminal-based AI Agent built with **LangChain**, **Mistral AI**, **OpenWeatherMap**, and **Tavily News API**. The agent assists users with real-time weather updates and news for Pakistani cities while incorporating a **Human-in-the-Loop (HITL)** approval middleware.

---

## 🌟 Key Features

- 🌤️ **Weather Intelligence:** Fetches real-time weather metrics via the OpenWeatherMap API.
- 📰 **News Intelligence:** Searches for the latest city news using Tavily Search API.
- 🛡️ **Human-in-the-Loop Middleware:** Custom `@wrap_tool_call` decorator that prompts the user for explicit confirmation (`yes/no`) before executing sensitive tool calls.
- 🔄 **Autonomous ReAct Agent Loop:** Built using LangChain/LangGraph's high-level `create_agent` abstraction.
- ⚠️ **Resilient Error Handling:** Wraps external network calls in try-except blocks to keep the session alive during DNS or network failures.

---






## 🛠️ Project Architecture

```text
User Input ──> LangChain Agent (Mistral LLM)
                    │
                    ├──> Should call weather_tool? ──> [Middleware Approval Prompt] ──> OpenWeather API
                    │
                    └──> Should call get_news? ───> [Middleware Approval Prompt] ──> Tavily 
                    Search API







## 🚀 Deploying on Railway

The **Streamlit web UI** (`UIAgents.py`) is the main entry point and what you deploy on Railway.

### Steps

1. **Push this repo to GitHub** (it already points to `github.com/Azansoh/City-Intelligence-Agent`).
2. In [Railway](https://railway.app), click **New Project → Deploy from GitHub repo** and select this repo.
3. Add the environment variables in the **Variables** tab:
   - `OPENWEATHERMAP_API_KEY`
   - `TAVILY_API_KEY`
   - `MISTRAL_API_KEY`
4. Railway auto-detects the `Procfile` and runs:
   ```text
   streamlit run UIAgents.py --server.address 0.0.0.0 --server.port $PORT ...
   ```
5. Open the generated **Public Networking** URL and chat with the agent.

### Running locally

```bash
streamlit run UIAgents.py
```

---

## 📂 Project Structure

Here is the repository structure and what each script contains:

```text
GENERATIVE_AI_3/
├── .venv/                   # Python Virtual Environment
├── .env                     # Secret API keys (Excluded via .gitignore)
├── .gitignore               # Git rules to prevent uploading keys & venv
├── requirements.txt         # Dependencies list
├── Procfile                 # Railway start command (Streamlit web UI)
├── runtime.txt              # Python version for Railway
├── UIAgents.py              # MAIN: Streamlit web UI for the City Intelligence Agent
├── Agents.py                # Terminal ReAct City Intelligence Agent with HITL
├── Builtintool.py           # Examples using built-in LangChain tools like tavily
├── Customtool.py            # Custom tool creation using @tool decorator
├── parallelrunnable.py      # Parallel execution using RunnableParallel
├── runnablepassthrough.py   # Data passing using RunnablePassthrough
└── sequencerunnable.py      # Sequential chaining using RunnableSequence / LCEL