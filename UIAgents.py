import os
import requests
import streamlit as st
from dotenv import load_dotenv
from functools import wraps

from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from tavily import TavilyClient


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="City Intelligence System",
    page_icon="🌆",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: gray;
        margin-bottom: 30px;
    }

    .tool-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_tool" not in st.session_state:
    st.session_state.pending_tool = None

if "tool_result" not in st.session_state:
    st.session_state.tool_result = None


# ==================================================
# HUMAN APPROVAL DECORATOR
# ==================================================

def wrap_tool_call(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        tool_name = func.__name__

        # Store tool information
        st.session_state.pending_tool = {
            "name": tool_name,
            "args": kwargs
        }

        return func(*args, **kwargs)

    return wrapper


# ==================================================
# WEATHER FUNCTION
# ==================================================

def get_weather(city: str):

    try:

        url = "https://api.openweathermap.org/data/2.5/weather"

        params = {
            "q": f"{city},PK",
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            return f"Error: {response.json().get('message', 'Something went wrong')}"

        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"]
        }

    except Exception as e:

        return f"Failed to fetch weather data: {e}"


# ==================================================
# WEATHER TOOL
# ==================================================

@tool
def weather_tool(city: str):
    """
    Get the current weather of a Pakistani city.
    """

    return get_weather(city)


# ==================================================
# TAVILY NEWS CLIENT
# ==================================================

tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ==================================================
# NEWS TOOL
# ==================================================

@tool
def get_news(city: str) -> str:
    """
    Get the latest news about a Pakistani city.
    Use this tool when the user asks for recent or latest news.
    """

    try:

        response = tavily_client.search(

            query=f"latest news {city} Pakistan",

            topic="news",

            max_results=3,

            days=2
        )

        results = response.get("results", [])

        if not results:

            return f"No recent news found for {city}."

        news = []

        for article in results:

            news.append(

                f"""
Title: {article.get('title', 'N/A')}

Source: {article.get('url', 'N/A')}

Content:
{article.get('content', 'N/A')}
"""
            )

        return "\n\n---\n\n".join(news)

    except Exception as e:

        return f"Unable to fetch news: {e}"


# ==================================================
# MISTRAL MODEL
# ==================================================

llm = ChatMistralAI(
    model="mistral-small-2506"
)


# ==================================================
# CREATE AGENT
# ==================================================

agent = create_agent(

    model=llm,

    tools=[
        weather_tool,
        get_news
    ]
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🌆 City Intelligence")

    st.markdown("---")

    st.subheader("Available Tools")

    st.markdown("""
    🌤️ **Weather Intelligence**

    Get current weather information
    for Pakistani cities.

    📰 **News Intelligence**

    Get the latest news about
    Pakistani cities.
    """)

    st.markdown("---")

    st.subheader("Example Questions")

    examples = [

        "What is the weather in Lahore?",

        "Tell me the latest news about Islamabad",

        "What is happening in Karachi today?",

        "What is the weather in Faisalabad?"
    ]

    for example in examples:

        if st.button(
            example,
            use_container_width=True
        ):

            st.session_state.example_prompt = example


    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ==================================================
# MAIN UI
# ==================================================

st.markdown(
    '<div class="main-title">🌆 City Intelligence System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your AI-powered assistant for Pakistani cities</div>',
    unsafe_allow_html=True
)


# ==================================================
# DISPLAY CHAT HISTORY
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# ==================================================
# HANDLE EXAMPLE PROMPT
# ==================================================

prompt = None

if "example_prompt" in st.session_state:

    prompt = st.session_state.example_prompt

    del st.session_state.example_prompt


# ==================================================
# CHAT INPUT
# ==================================================

user_input = st.chat_input(
    "Ask about weather or latest city news..."
)

if user_input:

    prompt = user_input


# ==================================================
# PROCESS USER MESSAGE
# ==================================================

if prompt:

    # Add user message
    st.session_state.messages.append({

        "role": "user",

        "content": prompt
    })


    # Display user message
    with st.chat_message("user"):

        st.markdown(prompt)


    # Assistant response
    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 Thinking..."
        ):

            try:

                result = agent.invoke({

                    "messages": [

                        {
                            "role": "system",

                            "content": """
You are a helpful City Intelligence Assistant.

Your job is to help users with:

1. Current weather of Pakistani cities.
2. Latest news about Pakistani cities.

IMPORTANT RULES:

- Use weather_tool when the user asks about weather.
- Use get_news when the user asks about recent or latest news.
- If the user asks a general question, answer normally.
- Keep responses clear and helpful.
"""
                        },

                        {
                            "role": "user",

                            "content": prompt
                        }
                    ]
                })


                # Get final response
                last_message = result["messages"][-1]

                response = last_message.content


                # Display response
                st.markdown(response)


                # Save assistant message
                st.session_state.messages.append({

                    "role": "assistant",

                    "content": response
                })


            except Exception as e:

                error_message = f"❌ Error: {str(e)}"

                st.error(error_message)

                st.session_state.messages.append({

                    "role": "assistant",

                    "content": error_message
                })