import json
import os
from system.conf import get_all_agents, get_available_models, update_model

COMMANDS_PATH = os.path.join(os.path.dirname(__file__), "commands.json")

with open(COMMANDS_PATH, "r") as f:
    commands = json.load(f)

VALID_AGENTS = commands.get("agents", ["jarvis", "coder"])


def get_commands():
    return commands


def list_all_models():
    """Return a formatted string of all available models grouped by agent and provider."""
    agents = get_all_agents()
    lines = ["📋 **Available Models:**\n"]

    for agent_name in VALID_AGENTS:
        if agent_name not in agents:
            continue
        available = agents[agent_name].get("available", {})
        lines.append(f"### {agent_name}")
        for provider, model_list in available.items():
            lines.append(f"  **{provider}**")
            for model in model_list:
                lines.append(f"    - `{model}`")
        lines.append("")

    return "\n".join(lines)


def list_models_by_agent(agent: str):
    """Return a formatted string of models for a specific agent."""
    agent = agent.lower()
    if agent not in VALID_AGENTS:
        return f"❌ Unknown agent `{agent}`. Available agents: {', '.join(VALID_AGENTS)}"

    models = get_available_models(agent=agent)
    lines = [f"📋 **Models for {agent}:**\n"]
    for provider, model_list in models.items():
        lines.append(f"  **{provider}**")
        for model in model_list:
            lines.append(f"    - `{model}`")
    return "\n".join(lines)


def list_models_by_agent_and_provider(agent: str, provider: str):
    """Return a formatted string of models for a specific agent and provider."""
    agent = agent.lower()
    provider = provider.lower()

    if agent not in VALID_AGENTS:
        return f"❌ Unknown agent `{agent}`. Available agents: {', '.join(VALID_AGENTS)}"

    models = get_available_models(agent=agent)
    if provider not in models:
        available = ", ".join(models.keys())
        return f"❌ Unknown provider `{provider}` for `{agent}`. Available providers: {available}"

    lines = [f"📋 **Models for {agent} ({provider}):**\n"]
    for model in models[provider]:
        lines.append(f"  - `{model}`")
    return "\n".join(lines)


def get_status():
    """Return the current system status: active models, providers, and config."""
    agents = get_all_agents()
    lines = ["📊 **System Status:**\n"]

    for agent_name in VALID_AGENTS:
        if agent_name not in agents:
            continue
        agent_conf = agents[agent_name]
        active = agent_conf.get("active", agent_conf.get("default", {}))
        lines.append(f"**{agent_name}**")
        lines.append(f"  - Provider: `{active.get('provider', 'N/A')}`")
        lines.append(f"  - Model: `{active.get('model', 'N/A')}`")
        lines.append(f"  - Status: 🟢 Active")
        lines.append("")

    return "\n".join(lines)


def change_model(agent: str, provider: str, model: str):
    """Change the active model for a given agent. Returns a confirmation or error message."""
    agent = agent.lower()
    provider = provider.lower()

    if agent not in VALID_AGENTS:
        return f"❌ Unknown agent `{agent}`. Available agents: {', '.join(VALID_AGENTS)}"

    models = get_available_models(agent=agent)

    if provider not in models:
        available = ", ".join(models.keys())
        return f"❌ Unknown provider `{provider}` for `{agent}`. Available providers: {available}"

    if model not in models[provider]:
        available = ", ".join(f"`{m}`" for m in models[provider])
        return f"❌ Model `{model}` not found for `{agent}` on `{provider}`. Available: {available}"

    update_model(agent, provider, model)
    return f"✅ `{agent}` model changed to `{model}` on `{provider}`"


def get_help():
    """Return a formatted help message with all available commands."""
    cmds = commands['commands']
    lines = ["💡 **Available Commands:**\n"]
    for cmd, info in cmds.items():
        lines.append(f"**`{cmd}`** — {info['description']}")
        lines.append(f"  Usage: `{info['usage']}`")
        lines.append("")
    return "\n".join(lines)


def handle_command(raw_input: str):
    """
    Parse and execute a slash command from user input.
    Returns (True, response_text) if it was a command,
    or (False, None) if the input is not a command.
    """
    raw_input = raw_input.strip()
    if not raw_input.startswith("/"):
        return False, None

    parts = raw_input.split()
    cmd = parts[0].lower()

    if cmd == "/model":
        if len(parts) < 4:
            return True, "⚠️ Usage: `/model <agent> <provider> <model>`\nExample: `/model jarvis ollama gpt-oss:20b`"
        agent = parts[1]
        provider = parts[2]
        model = parts[3]
        return True, change_model(agent, provider, model)

    elif cmd == "/models":
        if len(parts) >= 3:
            return True, list_models_by_agent_and_provider(parts[1], parts[2])
        elif len(parts) == 2:
            return True, list_models_by_agent(parts[1])
        return True, list_all_models()

    elif cmd == "/status":
        return True, get_status()

    elif cmd == "/help":
        return True, get_help()

    else:
        return True, f"❌ Unknown command `{cmd}`. Type `/help` to see available commands."