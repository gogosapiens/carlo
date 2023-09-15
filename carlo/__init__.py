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

def shorten_arg_names(word_list):
    shortened = {}
    words = list(word_list)
    for word in words:
        if word == "app_id":
            shortened[word] = "app_id"
            continue
        short_word = ""
        for i, char in enumerate(word):
            if i == 0:
                short_word += char
            else:
                is_similar_to_others = False
                for other_word in words:
                    if other_word != word and other_word.startswith(word[:i]):
                        is_similar_to_others = True
                        break
                if is_similar_to_others:
                    short_word += char
                else:
                    break
        shortened[word] = short_word
    return shortened

def shorten_arg_value(value):
    input_string = str(value)
    max_length = 16
    if len(input_string) > max_length:

        # Вычисляем количество символов, которые нужно оставить с обоих сторон строки
        left_chars = (max_length - 3) // 2
        right_chars = max_length - 3 - left_chars
        shortened_string = input_string[:left_chars] + "..." + input_string[-right_chars:]
        return shortened_string
    else:
        return input_string

def shorten_phase(phase):
    phase_length = 10
    if len(phase) > phase_length:
        return phase[:(phase_length - 3)] + "..."
    else:
        return phase + " " * (phase_length - len(phase))

# class Log:
#     phases = {}
#     constant_args = None
#     phase_counter = 0

#     @classmethod
#     def phase1(cls, phase):
#         cls.phases["1"] = [phase]

#     @classmethod
#     def phase2(cls, phase):
#         cls.phases.append(phase)

#     @classmethod
#     def phase3(cls, phase):
#         cls.phases.append(phase)
#         cls.phase_counter += 1

#     @classmethod
#     def clear_phases(cls):
#         cls.phases = []

#     @classmethod
#     def set_args(cls, args):
#         cls.constant_args = args
    
#     @classmethod
#     def print(cls, text, args=None):
#         frame_info = inspect.stack()[1]
#         file_name = "/".join(frame_info.filename.split('/')[-2:])
#         string = f"{file_name}: "

#         current_args = None
#         if args != None:
#             current_args = args
#         elif cls.constant_args != None:
#             current_args = cls.constant_args
#         else:
#             current_args = {}
        
#         shortened_args = shorten_arg_names(current_args.keys())

#         for key, value in current_args.items():
#             string += f"[{shortened_args[key]}: {shorten_arg_value(value)}] "

#         for phase in cls.phases:
#             string += f"> {phase.upper()} "

#         print(f"{string}> {text}")

def printc(text, phase=None, args=None):
    frame_info = inspect.stack()[1]
    file_name = frame_info.filename.split('/')[-1]
    string = f"[{file_name}]: "

    if isinstance(args, dict):
        shortened_args = shorten_arg_names(args.keys())
        for key, value in args.items():
            string += f"[{shortened_args[key]}: {shorten_arg_value(value)}] "
            
    elif isinstance(args, list):
        for arg in args:
            string += f"[{shorten_arg_value(arg)}] "

    if phase != None:
        string += f"<{phase.upper()}> "
    string += text
    print(string)
    
