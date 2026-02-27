from langchain_core.tools import tool

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


tools = [weather_api, get_location]
