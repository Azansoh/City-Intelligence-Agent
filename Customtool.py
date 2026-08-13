from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from rich import print


@tool
def get_input_length(input_string: str) -> int:
    """Calculates and returns the total word count of an input string."""
    return len(input_string.split())



# Initialize Model and Tools
llm = ChatMistralAI(model="mistral-small-2506")
tools_list = [get_input_length]
llm_with_tools = llm.bind_tools(tools_list)

# Map tool names to actual function objects
tools_by_name = {t.name: t for t in tools_list}

# Chat Memory / Message Stack
messages = []

user_prompt = input("You : ")
messages.append(HumanMessage(content=user_prompt))

# First invocation (LLM decides if it needs tools)
response = llm_with_tools.invoke(messages)
messages.append(response)

# Execute tool calls if requested by LLM
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        
        if tool_name in tools_by_name:
            # Invoking the tool with the tool_call dict automatically returns a ToolMessage
            tool_message = tools_by_name[tool_name].invoke(tool_call)
            messages.append(tool_message)

    # Second invocation (LLM responds after receiving tool execution results)
    final_response = llm_with_tools.invoke(messages)
    print(final_response.content)
else:
    # Print direct response if no tool was needed
    print(response.content)