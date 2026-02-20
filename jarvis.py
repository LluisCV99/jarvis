from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from operator import add
from langgraph.prebuilt import ToolNode
from tools import tools

class JarvisState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    errors: Annotated[Sequence[str], add]
    max_calls: int
    call_count: int

#ollama = ChatOllama(model="qwen3-coder:30b")
ollama = ChatOllama(model="gpt-oss:20b")


llm_with_tools = ollama.bind_tools(tools.tools)

def call_jarvis(state: JarvisState) -> dict:
    '''Calls the LLM with the current messages and returns the response.'''

    try:
        current_call_count = state.get('call_count', 0)
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

    if state['call_count'] >= state['max_calls']:
        print("Max call count reached, ending.")
        return 'END'
    if state['messages'][-1].tool_calls:
        print("Router: El model vol fer servir una eina. Anant a 'tools'...")
        return 'tools'
    return 'END'


tool_node = ToolNode(tools.tools)

graph = StateGraph(JarvisState)
graph.add_node('call_jarvis', call_jarvis)
graph.add_node('tools', tool_node)
graph.add_conditional_edges('call_jarvis', router, { 'END': END, 
                                                    'tools': 'tools',
                                                    'call_jarvis': 'call_jarvis' })
graph.set_entry_point('call_jarvis')

graph.add_edge('tools', 'call_jarvis')


jarvis = graph.compile()

inputs = {
    'messages': [
        SystemMessage(content="You are Jarvis, a helpful assistant."), 
        HumanMessage(content=input("Pregunta a Jarvis? "))
        ],
    'errors': [],
    'max_calls': 6,
    'call_count': 0
}
resposta = jarvis.invoke(inputs)

print(resposta['messages'][-1].content)