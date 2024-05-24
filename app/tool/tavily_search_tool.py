from langchain_community.tools.tavily_search import TavilySearchResults

tavily_search = TavilySearchResults(max_results=15, description='If No good result was found, Use this tool')