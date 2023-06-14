import json

def meta():
    try:
        with open("project/meta.json", "r") as f:
            meta = json.load(f)
    except FileNotFoundError:
        meta = {}
    return meta

def user_input():
    with open("project/user-input.json", "r") as f:
        user_input = json.load(f)
    return user_input

def keys():
    with open("keys/keys.json", "r") as f:
        keys = json.load(f)
    return keys


def set_meta_value(value, key=""):
    meta = meta()
    meta[key] = value
    with open("project/meta.json", "w") as f:
        json.dump(self.meta, f)

def project_id(platform):
    project_id_prefix = user_input["project_id_prefix"]
    return f"{project_id_prefix}.{platform}"