from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from operator import add
from langgraph.prebuilt import ToolNode
from supervisor.tools import tools
from dotenv import load_dotenv
from system.commands import handle_command
from system.conf import get_jarvis

load_dotenv()

class JarvisState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    errors: Annotated[Sequence[str], add]
    max_calls: int
    call_count: int
    next_call: Literal['call_jarvis', 'call_coder', 'END']

jarvis = ChatOllama(model=get_jarvis())

llm_with_tools = jarvis.bind_tools(tools)

def start_router(state: JarvisState) -> str:
    '''Determines the first step based on the initial state.'''
    message = str(state['messages'][-1].content)
    print(f"Checking for command in message: {message}")
    if message.startswith('/'):
        print("Command detected, routing command...")        
        return 'command'
    print("No command detected, starting normal flow...")
    return "continue"


def call_jarvis(state: JarvisState) -> dict:
    '''Calls the LLM with the current messages and returns the response.'''

    try:
        current_call_count = state.get('call_count', 1)
        print(f"Calling Jarvis for the {current_call_count}th time.")
        response = llm_with_tools.invoke(state['messages'])
        content = response.content
        if content.endswith('call_coder'):
            clean_response = content.removesuffix('call_coder')
            return {
                'messages': [AIMessage(content=clean_response)],
                'coder_messages': [
                    SystemMessage(content=coder_prompt), 
                    HumanMessage(content=clean_response)
                ],
                'call_count': current_call_count + 1,
                'next_call': 'call_coder'
            }
        return {
            'messages': [response],
            'call_count': current_call_count + 1,
            'next_call': 'call_jarvis'
        }
    except Exception as e:
        errors = (str("Error calling Jarvis: " + str(e)))
        print(errors)
        return {
            'errors': [errors],
            'call_count': state.get('call_count', 1),
            'next_call': 'call_jarvis'
        }       


def router(state: JarvisState) -> str:
    '''Determines the next step based on the current state.'''

    if state['call_count'] >= state.get('max_calls', 5):
        print("Max call count reached, ending.")
        return 'END'

    if state['next_call'] == 'call_coder':
        return 'call_coder'

    messages = state.get('messages', [])
    last_ai_msg = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)

    if last_ai_msg and hasattr(last_ai_msg, "tool_calls") and last_ai_msg.tool_calls:
        print("Router: The model wants to use a tool.")
        return 'tools'
    
    return 'END'


def action_command(state: JarvisState):
    '''Checks if the current message is a command.'''
    print(handle_command(str(state['messages'][-1].content)))


def call_coder(state: JarvisState) -> dict:
    '''Calls the coder model with the current messages and returns the response.'''
    try:
        response = coder.invoke(state['coder_messages'])
        return {
            'coder_messages': [],
            'messages': [HumanMessage(content=f"Coder response: {response.content}")],
            'next_call': 'call_jarvis'
        }
    except Exception as e:
        errors = (str("Error calling Coder: " + str(e)))
        print(errors)
        return {
            'errors': [errors],
        }


tool_node = ToolNode(tools)

graph = StateGraph(JarvisState)
graph.add_node('action_command', action_command)
graph.add_node('call_jarvis', call_jarvis)
graph.add_node('call_coder', call_coder)
graph.add_node('tools', tool_node)
graph.add_conditional_edges(START, start_router, {'command': 'action_command',
                                                    'continue': 'call_jarvis' })
graph.add_conditional_edges('call_jarvis', router, { 'END': END, 
                                                    'tools': 'tools',
                                                    'call_coder': 'call_coder',
                                                    'call_jarvis': 'call_jarvis' })
#graph.set_entry_point('start_router')

graph.add_edge('tools', 'call_jarvis')
graph.add_edge('call_coder', 'call_jarvis')


jarvis_compiled = graph.compile()

with open("prompts/jarvis.md", 'r') as f:
    jarvis_prompt = f.read()

with open("prompts/coder.md", 'r') as f:
    coder_prompt = f.read() 

if __name__ == "__main__":
    inputs = {
        'messages': [
            SystemMessage(content=jarvis_prompt), 
            HumanMessage(content=input("Ask Jarvis: "))
            ],
        'errors': [],
        'max_calls': 6,
        'call_count': 0
    }
    resposta = jarvis_compiled.invoke(inputs)

    print(resposta['messages'][-1].content)