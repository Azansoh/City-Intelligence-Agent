import os
import requests
from functools import wraps
from dotenv import load_dotenv
from rich import print

from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from tavily import TavilyClient

load_dotenv()

# --------------------------------------------------
# Middleware / Approval Decorator
# --------------------------------------------------
def wrap_tool_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        confirm = input(f"Agent want to call {tool_name}, Approve? (yes/no): ")
        
        if confirm.lower().strip().startswith("y"):
            return func(*args, **kwargs)
        else:
            return "Permission denied by user. Tool call aborted."
            
    return wrapper

# --------------------------------------------------
# Weather Tool Setup
# --------------------------------------------------
WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

def get_weather(city: str):
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},PK",
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return f"Error: {response.json().get('message', 'Something went wrong')}"
        data = response.json()
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"]
        }
    except Exception as e:
        return f"Failed to fetch weather data: {e}"

@tool
@wrap_tool_call  # Intercepts weather calls for approval
def weather_tool(city: str):
    """
    Get the current weather of a Pakistani city.
    """
    return get_weather(city)

# --------------------------------------------------
# Tavily News Tool Setup
# --------------------------------------------------
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
@wrap_tool_call
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
                f"Title: {article.get('title', 'N/A')}\n"
                f"Source: {article.get('url', 'N/A')}\n"
                f"Content: {article.get('content', 'N/A')}\n"
            )
        return "\n---\n".join(news)
    except Exception as e:
        return f"Unable to fetch news due to a connection error: {e}"

# --------------------------------------------------
# Agent Setup
# --------------------------------------------------
llm = ChatMistralAI(model="mistral-small-2506")





# tools = {
#     "weather_tool": weather_tool,
#     "get_news": get_news
# }   


# llm_with_tool = llm.bind_tools(
#     [weather_tool, get_news]
# )


# # --------------------------------------------------
# # Agent Loop
# # --------------------------------------------------

# message = []

# print("City Intelligence System")
# print("Type Exit for exit")


# while True:

#     user_input = input("You : ")

#     if user_input.lower() == "exit":
#         break

#     message.append(
#         HumanMessage(content=user_input)
#     )

#     while True:

#         result = llm_with_tool.invoke(message)

#         message.append(result)

#         # If tool is required
#         if result.tool_calls:

#             for tool_call in result.tool_calls:

#                 tool_name = tool_call["name"]

#                 # Human in the Loop
#                 confirm = input(
#                     f"Agent wants to call {tool_name}. "
#                     f"Approve (yes/no): "
#                 )

#                 if confirm.lower() == "no":

#                     print(
#                         "Tool call permission denied and "
#                         "I cannot send the latest information."
#                     )

#                     break

#                 tool_result = tools[tool_name].invoke(
#                     tool_call["args"]
#                 )

#                 message.append(
#                     ToolMessage(
#                         content=str(tool_result),
#                         tool_call_id=tool_call["id"]
#                     )
#                 )

#             continue

#         else:

#             print(result.content)
#             break



agent = create_agent(
    model=llm,
    tools=[weather_tool, get_news],
)

print("City Intelligence System | type exit to quit\n")

while True:
    user_input = input("You : ")
    if user_input.lower() == "exit":
        break

    # Put both system and user messages inside ONE 'messages' array
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": "You are a helpful city assistant."},
            {"role": "user", "content": user_input}
        ]
    })

    last_message = result["messages"][-1].content
    print(f"\nAssistant:\n{last_message}\n")