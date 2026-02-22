from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI

import getpass
import os
from dotenv import load_dotenv

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
    

#coder = ChatGoogleGenerativeAI(model="gemini-flash-latest")
#coder = ChatOllama(model="gpt-oss:20b")
coder = ChatOllama(model="qwen3-coder:30b")


@tool("add_numbers")
def add_numbers(a: int, b: int) -> int:
    '''Adds two numbers together.'''

    print('Calling adder')
    return a + b

@tool("get_Weather")
def weather_api(location: str) -> str:
    '''Gets the current weather for a given location.'''

    print('Calling weather API')
    return f"The current weather in {location} is night with a high of 15°C."

@tool("get_location")
def get_location() -> str:
    '''Returns the current location of the user.'''

    print('Calling location API')
    return "You are in Barcelona."

@tool("call_coder")
def call_coder(prompt: str) -> str:
    '''Calls the LLM expert coder.'''

    print('Calling coder')

    try:
        response = coder.invoke(prompt)
        return response.content
        
    except Exception as e:
        error_message = f"Error calling coder: {str(e)}"
        print(error_message)
        return error_message

tools = [add_numbers, weather_api, get_location, call_coder]
