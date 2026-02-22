import json
import shutil
import os

CONF_PATH = os.path.join(os.path.dirname(__file__), "conf.json")

def get_jarvis(config_path=CONF_PATH):
    with open(config_path, "r") as f:
        conf = json.load(f)
    return conf["agents"]["jarvis"]["active"] or conf["agents"]["jarvis"]["default"]

def get_coder(config_path=CONF_PATH):
    with open(config_path, "r") as f:
        conf = json.load(f)
    return conf["agents"]["coder"]["active"] or conf["agents"]["coder"]["default"]

def get_all_agents(config_path=CONF_PATH):
    """Return the full agents dict from conf.json."""
    with open(config_path, "r") as f:
        conf = json.load(f)
    return conf["agents"]

def get_available_models(agent: str = None, config_path=CONF_PATH):
    """
    Return available models. If agent is specified, return models for that agent.
    Otherwise, merge available models across all agents.
    """
    with open(config_path, "r") as f:
        conf = json.load(f)

    agents = conf["agents"]

    if agent and agent in agents:
        return agents[agent].get("available", {})

    # Merge available models from all agents
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
    with open(config_path, "r") as f:
        conf = json.load(f)
        
    conf["agents"][model_type]["active"] = {"provider": provider_name, "model": model_name}
    
    with open(config_path, "w") as f:
        json.dump(conf, f, indent=4)

def create_backup(config_path=CONF_PATH, backup_path=None):
    if backup_path is None:
        backup_path = config_path.replace(".json", "_backup.json")
    shutil.copy(config_path, backup_path)

def restore_backup(config_path=CONF_PATH, backup_path=None):
    if backup_path is None:
        backup_path = config_path.replace(".json", "_backup.json")
    shutil.copy(backup_path, config_path)