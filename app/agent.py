from langchain.agents import create_openai_functions_agent, AgentExecutor, create_json_chat_agent
from app import llms, prompt
import app.tool.naver_search_tool as naver_search_tool
import app.tool.google_search_tool as google_search_tool
import app.tool.tavily_search_tool as taviliy_search_tool
import os



os.environ["LANGCHAIN_PROJECT"] = "default"

tools = [google_search_tool.google_search, naver_search_tool.NaverSearchTool(description='If you can\'t find anything with google_search, use this tool')]

llama3_agent_executor = AgentExecutor(
    agent=create_json_chat_agent(llms.llama3, tools, prompt.json_prompt),
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

gpt_agent_executor = AgentExecutor(
    agent=create_openai_functions_agent(llms.gpt, tools, prompt.google_search_tool_prompt), 
    tools=tools, 
    verbose=True)
