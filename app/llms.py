from langchain_openai import ChatOpenAI
import os


gpt = ChatOpenAI(
    model="gpt-3.5-turbo", 
    api_key=os.environ.get('OPENAI_API_KEY'),
    temperature=0
)

llama3 = ChatOpenAI(
    base_url = "http://sionic.chat:8001/v1",
    api_key = os.environ.get('LLAMA3_API_KEY'),
    model="xionic-ko-llama-3-70b",
    verbose=True,
    temperature=0
)

eeve = ChatOpenAI(
    base_url='http://localhost:1234/v1',
    api_key=os.environ.get('EEVE_API_KEY'),
    model='teddylee777/EEVE-Korean-Instruct-10.8B-v1.0-gguf',
    temperature=0
)



