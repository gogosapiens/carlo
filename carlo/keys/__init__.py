import json

def keys():
    with open("keys/keys.json", "r") as f:
        keys = json.load(f)
    return keys

