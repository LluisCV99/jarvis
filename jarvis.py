from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from operator import add
from langgraph.prebuilt import ToolNode
from tools import tools
from dotenv import load_dotenv
from system.commands import handle_command

load_dotenv()

class JarvisState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    errors: Annotated[Sequence[str], add]
    max_calls: int
    call_count: int

jarvis = ChatOllama(model="qwen3-coder:30b")
#jarvis = ChatOllama(model="gpt-oss:20b")


llm_with_tools = jarvis.bind_tools(tools)

def call_jarvis(state: JarvisState) -> dict:
    '''Calls the LLM with the current messages and returns the response.'''

    try:
        current_call_count = state.get('call_count', 1)
        print(f"Calling Jarvis for the {current_call_count}th time.")
        response = llm_with_tools.invoke(state['messages'])
        return {
            'messages': [response],
            'call_count': current_call_count + 1
        }
    except Exception as e:
        errors = (str("Error calling Jarvis: " + str(e)))
        print(errors)
        return {
            'errors': [errors],
            'call_count': state.get('call_count', 0)
        }       


def router(state: JarvisState) -> str:
    '''Determines the next step based on the current state.'''

    if state['call_count'] >= state.get('max_calls', 5):
        print("Max call count reached, ending.")
        return 'END'
    if state['messages'][-1].tool_calls:
        print("Router: The models wants to use a tool. Going to 'tools'...")
        return 'tools'
    return 'END'

def start_router(state: JarvisState) -> str:
    '''Determines the first step based on the initial state.'''
    message = str(state['messages'][-1].content)
    print(f"Checking for command in message: {message}")
    if message.startswith('/'):
        print("Command detected, routing command...")        
        return 'command'
    print("No command detected, starting normal flow...")
    return "continue"


def action_command(state: JarvisState):
    '''Checks if the current message is a command.'''
    print(handle_command(str(state['messages'][-1].content)))
    


tool_node = ToolNode(tools)

graph = StateGraph(JarvisState)
graph.add_node('action_command', action_command)
graph.add_node('call_jarvis', call_jarvis)
graph.add_node('tools', tool_node)
graph.add_conditional_edges(START, start_router, {'command': 'action_command',
                                                    'continue': 'call_jarvis' })
graph.add_conditional_edges('call_jarvis', router, { 'END': END, 
                                                    'tools': 'tools',
                                                    'call_jarvis': 'call_jarvis' })
#graph.set_entry_point('start_router')

graph.add_edge('tools', 'call_jarvis')


jarvis_compiled = graph.compile()

with open("prompts/jarvis.md", "r") as f:
    JARVIS_SYSTEM_PROMPT = f.read()

with open("prompts/coder.md", "r") as f:
    CODER_SYSTEM_PROMPT = f.read()

if __name__ == "__main__":
    inputs = {
        'messages': [
            SystemMessage(content=JARVIS_SYSTEM_PROMPT), 
            HumanMessage(content=input("Ask Jarvis: "))
            ],
        'errors': [],
        'max_calls': 6,
        'call_count': 0
    }
    resposta = jarvis_compiled.invoke(inputs)

    print(resposta['messages'][-1].content)