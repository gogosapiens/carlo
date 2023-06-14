import json
import sys
import subprocess
import inspect

def input_json():
    with open(f'{sys.argv[0]}-input.json', 'r') as f:
        input_json = json.load(f)
    return input_json

def output_json(script_path):
    try:
        with open(f'{script_path}-output.json', 'r') as f:
            output_json = json.load(f)
        return output_json
    except FileNotFoundError:
        return None

def set_input_json(script_path, input_json):
    with open(f'{script_path}-input.json', 'w') as f:
        json.dump(input_json, f)

def set_output_json(output_json):
    with open(f'{sys.argv[0]}-output.json', 'w') as f:
        json.dump(output_json, f)


def call(script_path, input_json):
    set_input_json(script_path, input_json)
    process = subprocess.Popen(["python3", script_path])
    return_code = process.wait()
    if return_code != 0:
        print(f"{script_path} calling error")
        assert True
    return output_json(script_path)

def printc(text, phase=None):
    frame_info = inspect.stack()[1]
    file_name = frame_info.filename.split('/')[-1]
    if phase is None:
        print(f"[{file_name}]: {text}")
    else:
        print(f"[{file_name}]: [{phase.upper()}] {text}")
