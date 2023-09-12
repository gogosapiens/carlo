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

def printme(text):
    print(text)

def shorten_words(word_list):
    shortened = {}
    for word in word_list:
        if word == "app_id":
            shortened[word] = "app_id"
            continue
        short_word = ""
        for i, char in enumerate(word):
            if i == 0:
                short_word += char
            elif word[:i] not in word_list:
                short_word += char
            else:
                continue
        shortened[word] = short_word
    return shortened

def printc(text, phase=None, args=None):

    shortened_args = shorten_words(args.keys())

    frame_info = inspect.stack()[1]
    file_name = frame_info.filename.split('/')[-1]
    string = f"[{file_name}]: "
    if phase != None:
        string += f"[{phase.upper()}] "

    if isinstance(args, dict):
        for key, value in args.items():
            string += f"[{shortened_args[key]}: {value}] "
            
    elif isinstance(args, list):
        for arg in args:
            string += f"[{arg}] "

    string += text
    print(string)
    
