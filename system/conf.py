"""
Configuration module for Jarvis multi-agent system.

Manages agent configuration (models, providers, reasoning levels) from conf.json.
Provides LangChain tools so the supervisor can modify its own parameters at runtime.
"""

import json
import shutil
import os
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

CONF_PATH = os.path.join(os.path.dirname(__file__), "conf.json")


def _load_conf(config_path=CONF_PATH):
    """Load and return the full configuration dict from conf.json."""
    with open(config_path, "r") as f:
        return json.load(f)


def _save_conf(conf, config_path=CONF_PATH):
    """Write the configuration dict back to conf.json."""
    with open(config_path, "w") as f:
        json.dump(conf, f, indent=4)


def get_jarvis(config_path=CONF_PATH):
    """Return the active (or default) model config dict for the jarvis agent."""
    conf = _load_conf(config_path)
    return conf["agents"]["jarvis"]["active"] or conf["agents"]["jarvis"]["default"]


def get_coder(config_path=CONF_PATH):
    """Return the active (or default) model config dict for the coder agent."""
    conf = _load_conf(config_path)
    return conf["agents"]["coder"]["active"] or conf["agents"]["coder"]["default"]


def get_all_agents(config_path=CONF_PATH):
    """Return the full agents dict from conf.json, keyed by agent name."""
    conf = _load_conf(config_path)
    return conf["agents"]


def get_available_models(agent: str = None, config_path=CONF_PATH):
    """Return available models grouped by provider.

    If agent is specified, return only models for that agent.
    Otherwise, merge available models across all agents.
    """
    conf = _load_conf(config_path)
    agents = conf["agents"]

    if agent and agent in agents:
        return agents[agent].get("available", {})

    merged = {}
    for agent_conf in agents.values():
        for provider, models in agent_conf.get("available", {}).items():
            if provider not in merged:
                merged[provider] = []
            for m in models:
                if m not in merged[provider]:
                    merged[provider].append(m)
    return merged


def update_model(model_type: str, provider_name: str, model_name: str, config_path=CONF_PATH):
    """Update the active model for a given agent in conf.json."""
    conf = _load_conf(config_path)
    conf["agents"][model_type]["active"] = {"provider": provider_name, "model": model_name}
    _save_conf(conf, config_path)


def create_backup(config_path=CONF_PATH, backup_path=None):
    """Create a backup copy of the current conf.json."""
    if backup_path is None:
        backup_path = config_path.replace(".json", "_backup.json")
    shutil.copy(config_path, backup_path)


def restore_backup(config_path=CONF_PATH, backup_path=None):
    """Restore conf.json from a previously created backup."""
    if backup_path is None:
        backup_path = config_path.replace(".json", "_backup.json")
    shutil.copy(backup_path, config_path)


def get_reasoning(agent_name: str, config_path=CONF_PATH):
    """Return the current reasoning level name (e.g. 'medium') for the given agent."""
    conf = _load_conf(config_path)
    return conf["agents"][agent_name].get("reasoning", "medium")


def get_reasoning_levels(config_path=CONF_PATH):
    """Return the dict mapping reasoning level names to budget_tokens values."""
    conf = _load_conf(config_path)
    return conf.get("reasoning_levels", {"off": 0, "low": 1024, "medium": 4096, "high": 16384})


def update_reasoning(agent_name: str, level: str, config_path=CONF_PATH):
    """Update the reasoning level for the given agent in conf.json."""
    conf = _load_conf(config_path)
    conf["agents"][agent_name]["reasoning"] = level
    _save_conf(conf, config_path)


def get_llm(agent_name: str, config_path=CONF_PATH):
    """Instantiate and return the correct ChatModel for the given agent.

    Reads the agent's provider, model, and reasoning level from config,
    then returns the appropriate LangChain ChatModel (ChatOllama or ChatGoogleGenerativeAI).
    For ollama models, reasoning budget_tokens are passed via extra_body.
    """
    conf = _load_conf(config_path)

    agent_conf = conf["agents"][agent_name]["active"] or conf["agents"][agent_name]["default"]
    provider = agent_conf["provider"]
    model = agent_conf["model"]

    # Get reasoning budget
    reasoning_level = conf["agents"][agent_name].get("reasoning", "medium")
    reasoning_levels = conf.get("reasoning_levels", {})
    budget_tokens = reasoning_levels.get(reasoning_level, 4096)

    if provider == "ollama":
        if budget_tokens > 0:
            return ChatOllama(
                model=model,
                extra_body={"options": {"num_ctx": 8192}, "think": True, "budget_tokens": budget_tokens}
            )
        return ChatOllama(model=model, extra_body={"think": False})
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ─── LangChain Tools (for the supervisor to call) ────────────────────────────

@tool("get_system_status")
def tool_get_status() -> str:
    """Get the current system status: active models, providers, and reasoning levels for all agents."""
    agents = get_all_agents()
    levels = get_reasoning_levels()
    lines = []
    for name, agent in agents.items():
        active = agent.get("active", agent.get("default", {}))
        reasoning = agent.get("reasoning", "medium")
        budget = levels.get(reasoning, "?")
        lines.append(f"{name}: provider={active.get('provider')}, model={active.get('model')}, reasoning={reasoning} ({budget} tokens)")
    return "\n".join(lines)


@tool("change_model")
def tool_change_model(agent: str, provider: str, model: str) -> str:
    """Change the active model for an agent. Agent must be 'jarvis' or 'coder'. Provider must be 'ollama' or 'google'."""
    available = get_available_models(agent=agent)
    if provider not in available:
        return f"Error: unknown provider '{provider}' for '{agent}'. Available: {', '.join(available.keys())}"
    if model not in available[provider]:
        return f"Error: model '{model}' not found for '{agent}' on '{provider}'. Available: {', '.join(available[provider])}"
    update_model(agent, provider, model)
    return f"Done. {agent} now uses {model} on {provider}."


@tool("change_reasoning_level")
def tool_change_reasoning(agent: str, level: str) -> str:
    """Change the reasoning level for an agent. Levels: 'off', 'low', 'medium', 'high'."""
    levels = get_reasoning_levels()
    if level not in levels:
        return f"Error: unknown level '{level}'. Available: {', '.join(levels.keys())}"
    update_reasoning(agent, level)
    return f"Done. {agent} reasoning set to {level} ({levels[level]} tokens)."


@tool("list_available_models")
def tool_list_models(agent: str = None) -> str:
    """List available models. Optionally filter by agent name ('jarvis' or 'coder')."""
    models = get_available_models(agent=agent)
    lines = []
    for provider, model_list in models.items():
        lines.append(f"{provider}: {', '.join(model_list)}")
    return "\n".join(lines)


config_tools = [tool_get_status, tool_change_model, tool_change_reasoning, tool_list_models]