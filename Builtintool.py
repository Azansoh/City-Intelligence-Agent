from dotenv import load_dotenv
load_dotenv()
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults




# Fix the class name instantiation:
search_tool = TavilySearchResults(max_result=5)

llm=ChatMistralAI(model="mistral-small-2506")



prompt = ChatPromptTemplate.from_template(
    """
You are a helpful assistant

summarize the following news into clear bullet points

{news}
"""
)


parser = StrOutputParser()


chain=prompt | llm | parser

new_result=search_tool.run("latest news about AI in 2026")

result = chain.invoke({"news": str(new_result)})

print(result)
print()
print()
print()
print()

print(search_tool.description)
print(search_tool.name)
print(search_tool.args)
