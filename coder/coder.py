from langgraph.prebuilt import create_react_agent
from coder.tools import tools
from system.conf import get_llm

with open("coder/prompts/coder.md", "r") as f:
    coder_prompt = f.read()

coder_agent = create_react_agent(
    model=get_llm("coder"),
    tools=tools,
    name="coder",
    prompt=coder_prompt,
)

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    user_input = input("Ask Coder: ")
    result = coder_agent.invoke({
        "messages": [HumanMessage(content=user_input)],
    })
    print(result["messages"][-1].content)
