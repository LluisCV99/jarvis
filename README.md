# Jarvis: Multi-LLM Agent Experiment

A learning experiment exploring the design and orchestration of **multi-agent systems** using multiple Large Language Models (LLMs). Jarvis demonstrates how to build agent architectures where different specialized LLMs collaborate, delegate tasks, and make decisions through a graph-based workflow.

## Roadmap

> Planned features and improvements:

- [x] **Model switching from UI/CLI** — Slash commands to change active models, list available models, and check system status directly from the Chat UI
- [ ] **Long-term memory** — Persistent conversation history and context across sessions
- [ ] **Camera access** — Integrate camera input so Jarvis can process visual information

## Project Goals

This project is an **educational experiment** designed to:

- Learn how to architect **agent systems with multiple LLMs** working together
- Understand LLM **tool-calling** and function invocation patterns
- Explore **agent routing and decision-making** using state machines (LangGraph)
- Implement **specialized agent roles** (e.g., general coordinator, code specialist)
- Study how agents can **delegate tasks** between different models and providers
- Experiment with **different model providers** (Ollama locally hosted, Google Gemini cloud)
- Build practical understanding of **agentic workflows** and autonomous reasoning

## Architecture

### Core Components

- **Jarvis (Main Agent)**: The orchestrator agent powered by a local Ollama model (`gpt-oss:20b`). Makes decisions, invokes tools, and coordinates the workflow.
  
- **Tool System**: A suite of tools that agents can invoke:
  - `add_numbers`: Basic arithmetic operations
  - `get_Weather`: Retrieves weather information for a given location
  - `get_location`: Gets user location
  - `call_coder`: Delegates coding tasks to a specialized LLM (Google Gemini)

- **Router**: Decision logic that determines the flow:
  - Routes to tool execution if the agent requests tool use
  - Routes to END if max iterations reached
  - Enables agentic loops and iterative problem-solving

- **LangGraph State Machine**: Manages the agent execution flow with typed state (`JarvisState`) containing:
  - `messages`: Conversation history
  - `errors`: Error tracking
  - `call_count`: Iteration counter
  - `max_calls`: Execution limit (default: 6)

- **Configuration Module (`conf.py`)**: A dedicated module for managing agent configurations with support for:
  - Reading active model configs (`get_jarvis`, `get_coder`)
  - Hot-swapping models at runtime (`update_model`)
  - Configuration backup and restore (`create_backup`, `restore_backup`)

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
  ├─→ [Tool: get_Weather]
  │   └─→ Returns weather data
  │
  ├─→ [Tool: call_coder - Specialized]
  │   └─→ [Gemini Model - Code Expert]
  │       └─→ Returns code solution
  │
  └─→ Synthesizes results → Output
```

The key learning: **Specialized LLMs for specialized tasks** - Ollama handles orchestration and decision-making, while Google Gemini is used for code generation.

## Project Structure

```
jarvis/
├── jarvis.py          # Main agent: graph definition, state, entry point
├── app.py             # Flask server for the web chat UI
├── tools.py           # Tool definitions (add_numbers, weather, location, call_coder)
├── system/
│   ├── conf.json      # Agent configuration (providers, models, defaults)
│   ├── conf.py        # Configuration management (read/update/backup models)
│   ├── commands.json  # Slash command definitions (usage, args, examples)
│   └── commands.py    # Command parsing, validation, and execution
├── templates/
│   └── chat.html      # Web chat interface
├── tests/
│   └── test_conf.py   # Test suite for the configuration module
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (API keys, not tracked in git)
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.10+
- Ollama running locally with models installed (`gpt-oss:20b` or similar)
- Google API key for Gemini (for the `call_coder` tool)

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

3. Set up environment variables:
```bash
# Create a .env file with your API key
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Dependencies

| Package | Purpose |
|---|---|
| `langchain` / `langchain-core` | LLM framework and abstractions |
| `langgraph` | State machine and agent orchestration |
| `langchain-ollama` | Ollama integration for local models |
| `langchain-google-genai` | Google Gemini integration |
| `ollama` | Ollama client library |
| `google-genai` | Google AI client library |
| `python-dotenv` | Environment variable management |
| `langsmith` | LLM observability and tracing |
| `aiohttp` / `httpx` | Async HTTP clients |
| `flask` | Web server for the chat UI |

### Configuration

Agent models are managed through `conf.json`. Each agent has a **default** config, an **active** config (can be changed at runtime), and a list of **available** models per provider:

```json
{
    "agents": {
        "jarvis": {
            "default": { "provider": "ollama", "model": "gpt-oss:20b" },
            "active": { "provider": "ollama", "model": "gpt-oss:20b" },
            "available": {
                "ollama": ["gpt-oss:20b", "gpt-oss:120b"],
                "google": ["gemini-flash-latest", "gemini-pro"]
            }
        },
        "coder": {
            "default": { "provider": "google", "model": "gemini-flash-latest" },
            "active": { "provider": "google", "model": "gemini-flash-latest" },
            "available": {
                "ollama": ["qwen3-coder:30b", "deepseek-coder:33b"],
                "google": ["gemini-flash-latest"]
            }
        }
    }
}
```

Use `conf.py` to manage models programmatically:

```python
import conf

# Get the active model for each agent
jarvis_config = conf.get_jarvis()   # {"provider": "ollama", "model": "gpt-oss:20b"}
coder_config = conf.get_coder()     # {"provider": "google", "model": "gemini-flash-latest"}

# Swap a model at runtime
conf.update_model("jarvis", "google", "gemini-pro")

# Backup and restore configuration
conf.create_backup()
conf.restore_backup()
```

### Running

**CLI mode** (original terminal interface):
```bash
python jarvis.py
```

**Chat UI** (web interface):
```bash
python app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Chat UI

The web interface (`app.py` + `templates/chat.html`) provides a browser-based chat experience with Jarvis:

- **Dark glassmorphism theme** with smooth animations and a typing indicator
- **Markdown rendering** — Jarvis responses are parsed and displayed as rich HTML using [marked.js](https://github.com/markedjs/marked), supporting headings, lists, tables, blockquotes, bold/italic, links, and more
- **Syntax-highlighted code blocks** via [highlight.js](https://highlightjs.org/) — fenced code blocks with language tags (e.g. ` ```python `) are automatically highlighted
- **Inline code styling** — backtick-wrapped code gets a subtle background
- **Responsive layout** — adapts to mobile screens
- **Send on Enter** — press Enter to send, Shift+Enter for newlines

## Slash Commands

Jarvis supports slash commands typed directly in the chat. Commands are intercepted in `app.py` **before** reaching the LLM, so they execute instantly.

| Command | Usage | Description |
|---------|-------|-------------|
| `/model` | `/model <agent> <provider> <model>` | Change the active model for an agent |
| `/models` | `/models [agent] [provider]` | List available models (optionally filtered) |
| `/status` | `/status` | Show active model and provider per agent |
| `/help` | `/help` | Show all available commands |

### Examples

```
/model jarvis ollama gpt-oss:120b     # Switch Jarvis to a larger model
/model coder google gemini-flash-latest  # Switch the coder agent
/models                                 # List all models for all agents
/models jarvis                          # List only Jarvis's available models
/models coder google                    # List coder's Google models
/status                                 # Check what's currently active
```

Command definitions live in `system/commands.json`. The handler logic in `system/commands.py` uses `system/conf.py` to read and update `system/conf.json`, keeping model data in a single source of truth.

## Testing

Run the configuration test suite:

```bash
python test_conf.py
```

This validates `get_jarvis`, `get_coder`, `update_model`, and `backup/restore` functionality using temporary test files.

## How It Works

1. **Input**: User sends a message via the chat UI or CLI
2. **Command Check**: If the message starts with `/`, it's intercepted and handled as a slash command (no LLM call)
3. **Agent Call**: Otherwise, send the prompt to Jarvis, which analyzes and decides next action
4. **Tool Invocation**: If Jarvis requests tool use, execute the appropriate tool
5. **Delegation**: For `call_coder`, delegate to Google Gemini for specialized tasks
6. **Iteration**: Router decides whether to loop (invoke agent again) or terminate
7. **Output**: Final response synthesized from the agent's reasoning

## Learning Outcomes

By working through this project, you'll understand:

1. **Agent Orchestration**: How to structure multi-agent systems with clear roles
2. **Tool Binding**: How LLMs invoke tools and pass structured data
3. **State Management**: Maintaining conversation context and agent state
4. **Routing Logic**: Decision trees and agentic flow control
5. **Multi-Model Coordination**: Delegating tasks between different LLMs
6. **Configuration Management**: Hot-swapping models and managing agent configs
7. **Error Handling**: Graceful failures in distributed agent systems
8. **Iteration Limits**: Preventing infinite loops in agentic reasoning

## Key Concepts Explored

- **Agent Autonomy**: Agents make decisions without explicit human direction
- **Tool-Calling LLMs**: Using function signatures to guide model behavior
- **Specialized Agents**: Different models for different domains (reasoning vs. coding)
- **Fallback Mechanisms**: Error handling and retry logic
- **Bounded Reasoning**: Iteration limits to ensure termination
- **Runtime Configurability**: Swapping models without code changes

## Extensibility

Easily extend Jarvis by:

1. Adding new tools in `tools.py`:
```python
@tool("my_tool")
def my_tool(param: str) -> str:
    '''Tool description'''
    return result
```

2. Updating `jarvis.py` to use new tools
3. Adding new models to `conf.json` under `available`
4. Swapping active models via `conf.update_model()`
5. Adding new specialized agents

## Notes

- This is an **experiment and learning project**, not production-ready code
- Ensure Ollama is running before executing
- Check console output for detailed execution traces
- Modify `max_calls` in `jarvis.py` to control iteration depth

## Educational Resources

This project demonstrates concepts from:
- Agent-based architecture patterns
- LangChain/LangGraph framework usage
- LLM fine-tuning and specialization
- Agentic reasoning and planning
- Tool-use in language models

---

**Created as a learning experiment to understand multi-LLM agent orchestration**
