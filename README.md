# Jarvis: Multi-LLM Agent Experiment

A learning experiment exploring the design and orchestration of **multi-agent systems** using multiple Large Language Models (LLMs). Jarvis demonstrates how to build agent architectures where different specialized LLMs collaborate, delegate tasks, and make decisions through a graph-based workflow.

## 🎯 Project Goals

This project is an **educational experiment** designed to:

- Learn how to architect **agent systems with multiple LLMs** working together
- Understand LLM **tool-calling** and function invocation patterns
- Explore **agent routing and decision-making** using state machines (LangGraph)
- Implement **specialized agent roles** (e.g., general coordinator, code specialist)
- Study how agents can **delegate tasks** between different models and providers
- Experiment with **different model providers** (Ollama locally hosted, Google Gemini cloud)
- Build practical understanding of **agentic workflows** and autonomous reasoning

## 🏗️ Architecture

### Core Components

- **Jarvis (Main Agent)**: The orchestrator agent powered by a local Ollama model (`gpt-oss:20b`). Makes decisions, invokes tools, and coordinates the workflow.
  
- **Tool System**: A suite of tools that agents can invoke:
  - `add_numbers`: Basic arithmetic operations
  - `get_weather`: Retrieves weather information
  - `get_location`: Gets user location
  - `call_coder`: Delegates coding tasks to a specialized LLM (Google Gemini)

- **Router**: Decision logic that determines the flow:
  - Routes to tool execution if the agent requests tool use
  - Routes to END if max iterations reached
  - Enables agentic loops and iterative problem-solving

- **LangGraph State Machine**: Manages the agent execution flow with typed state containing:
  - `messages`: Conversation history
  - `errors`: Error tracking
  - `call_count`: Iteration counter
  - `max_calls`: Execution limit

### Multi-LLM Strategy

```
Input
  ↓
[Jarvis Agent - Ollama Model]
  ├─→ Decides to use a tool
  │
  ├─→ [Tool: add_numbers]
  │   └─→ Returns result
  │
  ├─→ [Tool: get_weather]
  │   └─→ Returns weather data
  │
  ├─→ [Tool: call_coder - Specialized]
  │   └─→ [Gemini Model - Code Expert]
  │       └─→ Returns code solution
  │
  └─→ Synthesizes results → Output
```

The key learning: **Specialized LLMs for specialized tasks** - Ollama handles orchestration and decision-making, while Google Gemini is used for code generation.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Ollama running locally with models installed (`gpt-oss:20b` or similar)
- Google API key for Gemini (optional, if using the `call_coder` tool)

### Installation

1. Create a virtual environment:
```bash
python -m venv lang_env
lang_env\Scripts\activate  # On Windows
source lang_env/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The project uses:
- `langchain` and `langchain-core`: LLM framework
- `langgraph`: State machine and agent orchestration
- `langchain-ollama`: Ollama integration
- `langchain-google-genai`: Google Gemini integration

3. Set up environment variables:


### Create a .env file with your API key for example with the gemini api:
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Configuration

Edit `conf.json` to configure your LLM providers:

```json
{
    "models": {
        "jarvis": {
            "provider": {
                "ollama": {
                    "model": "gpt-oss:20b"
                }
            }
        },
        "coder": {
            "provider": {
                "ollama": {
                    "model": "gpt-oss:20b"
                }
            }
        }
    }
}
```

## 📚 Learning Outcomes

By working through this project, you'll understand:

1. **Agent Orchestration**: How to structure multi-agent systems with clear roles
2. **Tool Binding**: How LLMs invoke tools and pass structured data
3. **State Management**: Maintaining conversation context and agent state
4. **Routing Logic**: Decision trees and agentic flow control
5. **Multi-Model Coordination**: Delegating tasks between different LLMs
6. **Error Handling**: Graceful failures in distributed agent systems
7. **Iteration Limits**: Preventing infinite loops in agentic reasoning

## 🔍 How It Works

1. **Initialization**: Load Jarvis agent with tools and set initial state
2. **Agent Call**: Send prompt to Jarvis, which analyzes and decides next action
3. **Tool Invocation**: If Jarvis requests tool use, execute the appropriate tool
4. **Delegation**: For `call_coder`, delegate to Google Gemini for specialized tasks
5. **Iteration**: Router decides whether to loop (invoke agent again) or terminate
6. **Output**: Final response synthesized from the agent's reasoning

## 💡 Key Concepts Explored

- **Agent Autonomy**: Agents make decisions without explicit human direction
- **Tool-Calling LLMs**: Using function signatures to guide model behavior
- **Specialized Agents**: Different models for different domains (reasoning vs. coding)
- **Fallback Mechanisms**: Error handling and retry logic
- **Bounded Reasoning**: Iteration limits to ensure termination

## 🛠️ Extensibility

Easily extend Jarvis by:

1. Adding new tools in `tools.py`:
```python
@tool("my_tool")
def my_tool(param: str) -> str:
    '''Tool description'''
    return result
```

2. Updating `jarvis.py` to use new tools
3. Swapping models in `conf.json`
4. Adding new specialized agents

## 📝 Notes

- This is an **experiment and learning project**, not production-ready code
- Ensure Ollama is running before executing
- Check console output for detailed execution traces
- Modify `max_calls` to control iteration depth

## 🎓 Educational Resources

This project demonstrates concepts from:
- Agent-based architecture patterns
- LangChain/LangGraph framework usage
- LLM fine-tuning and specialization
- Agentic reasoning and planning
- Tool-use in language models

---

**Created as a learning experiment to understand multi-LLM agent orchestration** 🤖
