import json


def read_json_file(path_like: str) -> dict:
    """Read json file"""
    with open(path_like, "r") as f:
        return json.load(f)
