from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from operator import add
from langgraph.prebuilt import ToolNode
from coder.tools import tools
from dotenv import load_dotenv
from system.conf import get_coder

load_dotenv()

class CoderState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    errors: Annotated[Sequence[str], add]
    max_calls: int
    call_count: int

coder = ChatOllama(model=get_coder())

coder_with_tools = coder.bind_tools(tools)

def call_coder(state: CoderState) -> dict:

    current_call_count = state.get('call_count', 1)
    print(f"Calling Coder Agent for the {current_call_count}th time.")
    try:
        response = coder_with_tools.invoke(state['messages'])
        return {
            'messages': [response],
            'call_count': current_call_count + 1,
        }
    except Exception as e:
        errors = (str("Error calling Coder Agent: " + str(e)))
        print(errors)
        return {
            'errors': [errors],
            'call_count': current_call_count + 1,
        }

tool_node = ToolNode(tools)

graph = StateGraph(CoderState)
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


coder_compiled = graph.compile()

