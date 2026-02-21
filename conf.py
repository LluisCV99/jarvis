import json
import shutil

def get_jarvis(config_path="conf.json"):
    with open(config_path, "r") as f:
        conf = json.load(f)
    return conf["agents"]["jarvis"]["active"] or conf["agents"]["jarvis"]["default"]

def get_coder(config_path="conf.json"):
    with open(config_path, "r") as f:
        conf = json.load(f)
    return conf["agents"]["coder"]["active"] or conf["agents"]["coder"]["default"]

def update_model(model_type: str, provider_name: str, model_name: str, config_path="conf.json"):
    with open(config_path, "r") as f:
        conf = json.load(f)
        
    conf["agents"][model_type]["active"] = {"provider": provider_name, "model": model_name}
    
    with open(config_path, "w") as f:
        json.dump(conf, f, indent=4)

def create_backup(config_path="conf.json", backup_path="conf_backup.json"):
    shutil.copy(config_path, backup_path)

def restore_backup(config_path="conf.json", backup_path="conf_backup.json"):
    shutil.copy(backup_path, config_path)