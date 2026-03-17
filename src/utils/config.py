from pathlib import Path
import yaml


def load_yaml(path: str):
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_settings():
    return load_yaml("config/settings.yaml")


def load_scoring():
    return load_yaml("config/scoring.yaml")


def load_sources():
    data = load_yaml("config/sources.yaml")
    return data.get("sources", [])
