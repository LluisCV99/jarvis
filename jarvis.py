from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from operator import add
from langgraph.prebuilt import ToolNode
from tools import tools
from dotenv import load_dotenv

load_dotenv()

class JarvisState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    errors: Annotated[Sequence[str], add]
    max_calls: int
    call_count: int

#ollama = ChatOllama(model="qwen3-coder:30b")
jarvis = ChatOllama(model="gpt-oss:20b")


llm_with_tools = jarvis.bind_tools(tools)

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
        print("Router: The models wants to use a tool. Going to 'tools'...")
        return 'tools'
    return 'END'


tool_node = ToolNode(tools)

graph = StateGraph(JarvisState)
graph.add_node('call_jarvis', call_jarvis)
graph.add_node('tools', tool_node)
graph.add_conditional_edges('call_jarvis', router, { 'END': END, 
                                                    'tools': 'tools',
                                                    'call_jarvis': 'call_jarvis' })
graph.set_entry_point('call_jarvis')

graph.add_edge('tools', 'call_jarvis')


jarvis_compiled = graph.compile()

if __name__ == "__main__":
    inputs = {
        'messages': [
            SystemMessage(content="You are Jarvis, a helpful assistant. If you are ask to code or asked about code -> use the 'call_coder' tool to call the expert coder model. Always try to use the tools if they are relevant to the question."), 
            HumanMessage(content=input("Ask Jarvis: "))
            ],
        'errors': [],
        'max_calls': 6,
        'call_count': 0
    }
    resposta = jarvis_compiled.invoke(inputs)

    print(resposta['messages'][-1].content)