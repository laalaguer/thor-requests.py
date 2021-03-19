import json

def build_url(base: str, tail: str) -> str:
    ''' Build a proper URL, base + tail '''
    return base.rstrip('/') + '/' + tail.lstrip('/')


def read_json_file(path_like: str) -> dict:
    ''' Read json file '''
    with open(path_like, 'r') as f:
        return json.load(f)