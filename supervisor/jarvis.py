from langgraph_supervisor import create_supervisor
from coder.coder import coder_agent
from supervisor.tools import tools as jarvis_tools
from system.conf import get_llm, config_tools

with open("supervisor/prompts/jarvis.md", "r") as f:
    jarvis_prompt = f.read()

jarvis_compiled = create_supervisor(
    agents=[coder_agent],
    model=get_llm("jarvis"),
    prompt=jarvis_prompt,
    tools=jarvis_tools + config_tools,
).compile()

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    user_input = input("Ask Jarvis: ")
    result = jarvis_compiled.invoke({
        "messages": [HumanMessage(content=user_input)],
    })
    print(result["messages"][-1].content)