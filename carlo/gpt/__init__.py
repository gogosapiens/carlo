import json
from openai import OpenAI
import openai
import requests
from carlo import keychain
from carlo import printc
import time

client = OpenAI(api_key=keychain.keys()["openai_key"])

default_model = "gpt-3.5-turbo-1106"

def validate_response(response, validator):
	result = validator(response)
	if isinstance(result, bool):
		return result, response
	else:
		return True, result

def get_text(prompt, model=default_model, temperature=1, validator=None, optimizer=None, ranks=None, repeat_count=10, json_mode=False, seed=None, debug=False):
	if ranks is None:
		ranks = []

	if repeat_count < 0:
		printc("Repeat count exceeded. Returning best result.")
		return best_results(ranks)

	messages = [{"role": "user", "content": prompt}]
	def get_text_func():
		return get_text(
			prompt, 
			model=model, 
			temperature=temperature, 
			validator=validator, 
			optimizer=optimizer, 
			ranks=ranks.copy(), 
			repeat_count=repeat_count-1, 
			json_mode=json_mode,
			seed=seed,
			debug=debug
		)
	try: 
		if json_mode:
			if seed is not None:
				response = client.chat.completions.create(
					model=model,
					response_format={ "type": "json_object" },
					messages=messages,
					temperature=temperature,
					seed=seed,
				)
			else:
				response = client.chat.completions.create(
					model=model,
					response_format={ "type": "json_object" },
					messages=messages,
					temperature=temperature,
				)
		else:
			if seed is not None:
				response = client.chat.completions.create(
					model=model,
					messages=messages,
					temperature=temperature,
					seed=seed,
				)
			else:
				response = client.chat.completions.create(
					model=model,
					messages=messages,
					temperature=temperature,
				)	
	except openai.RateLimitError as e:
		retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
		printc(f"GPT rate limit exceeded. Retrying in {retry_time} seconds...")
		time.sleep(retry_time)
		return get_text_func()
	except openai.BadRequestError as e:
		printc(f"Bad GPT request: {e}")
		if e.code == "context_length_exceeded":
			printc(f"Retrying with model 'gpt-4'...")
			return get_text(
				prompt, 
				model="gpt-4-1106-preview", 
				temperature=temperature, 
				validator=validator, 
				optimizer=optimizer, 
				ranks=ranks.copy(), 
				repeat_count=repeat_count-1, 
				json_mode=json_mode,
				seed=seed,
				debug=debug
			)
		else:
			printc(f"Retrying in 30 seconds...")
			time.sleep(30)
			return get_text_func()
	except openai.OpenAIError as e:
		printc(f"Error from GPT: {e}")
		printc(f"Retrying in 30 seconds...")
		time.sleep(30)
		return get_text_func()
	except requests.exceptions.Timeout:
		printc("GPT request timed out. Retrying in 30 seconds...")
		time.sleep(30)
		return get_text_func()
	except Exception as e:
		printc(f"Unexpected GPT error occurred: {e}")
		return get_text_func()
	
	answer = response.choices[0].message.content
	if debug:
		printc(f"GPT model: {response.model}")
		printc(f"GPT system_fingerprint=: {response.system_fingerprint=}")
		printc(f"GPT usage: {response.usage}")

	if validator != None:
		ok, new_answer = validate_response(answer, validator)
		if ok:
			return get_text_optimizer_logic(answer, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count, json_mode, seed, debug)
		else:
			if repeat_count > 0:
				printc(f"Response didn't pass validation. Repeating GPT request...")
				return get_text_func()
			else:
				return best_results(ranks)
	else:
		return get_text_optimizer_logic(answer, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count, json_mode, seed, debug)
			
			
def get_text_optimizer_logic(response, prompt, model, temperature, validator, optimizer, ranks, repeat_count, json_mode, seed, debug):
	if optimizer != None:
		rank = optimizer(response)
		ranks.append((response, rank))
		if repeat_count > 0:
			printc(f"Optimizing score: {rank}. Repeating GPT request...")
			return get_text(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1, json_mode=json_mode, seed=seed, debug=debug)
		else:
			return best_results(ranks)
	else:
		return response
	
def get_json_optimizer_logic(response, prompt, model, temperature, validator, optimizer, ranks, repeat_count, seed, debug):
	if optimizer != None:
		rank = optimizer(response)
		ranks.append((response, rank))
		if repeat_count > 0:
			printc(f"Optimizing score: {rank}. Repeating GPT request...")
			return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1, seed=seed, debug=debug)
		else:
			return best_results(ranks)
	else:
		return response

def get_value(prompt, model=default_model, temperature=1, validator=None, optimizer=None, repeat_count=10, seed=None, debug=False):
	key = "value"
	prompt += f"Put result under the key '{key}' in json."
	validator_func = None
	if validator != None:
		validator_func = lambda x: key in x and validator(x[key])
	else:
		validator_func = lambda x: key in x

	optimizer_func = None
	if optimizer != None:
		optimizer_func = lambda x: optimizer(x[key])

	result = get_json(prompt, model=model, temperature=temperature, validator=validator_func, optimizer=optimizer_func, ranks=[], repeat_count=repeat_count, seed=seed, debug=debug)
	if result != None:
		return result[key] if (isinstance(result, dict) and key in result) else result
	else:
		return None

def best_results(ranks):
	if len(ranks) > 0:
		ranks.sort(key=lambda x: x[1], reverse=True)
		return ranks
	else:
		return None

def get_json(prompt, model=default_model, temperature=1, validator=None, optimizer=None, ranks=None, repeat_count=10, seed=None, debug=False):
	if ranks is None:
		ranks = []
	prompt += "\nDon't add any extra text. Return only JSON."
	json_str = get_text(prompt, model=model, temperature=temperature, repeat_count=repeat_count, json_mode=True, seed=seed, debug=debug)
	if json_str is None:
		if repeat_count > 0:
			printc("Repeating GPT request...")
			return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1, seed=seed, debug=debug)
		else:
			return best_results(ranks)
	try:
		json_data = json.loads(json_str)
		if validator != None:
			ok, new_json_data = validate_response(json_data, validator)
			if ok:
				return get_json_optimizer_logic(new_json_data, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count, seed, debug)
			else:
				if repeat_count > 0:
					printc(f"Response didn't pass validation. Repeating GPT request...")
					return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1, seed=seed, debug=debug)
				else:
					return best_results(ranks)
		else:
			return get_json_optimizer_logic(json_data, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count, seed, debug)

	except json.JSONDecodeError as e:
		if repeat_count > 0:
			printc(f"Error decoding GPT JSON: {e}")
			printc("Repeating GPT request...")
			return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1, seed=seed, debug=debug)
		else:
			printc(f"Error decoding GPT JSON: {e}")
			return best_results(ranks)
		
def translate(text, target_language, model=default_model, note="", validator=None, optimizer=None, repeat_count=10):
	prompt = f"Translate text into language {target_language}. {note}\nText: {text}\n"
	return get_value(prompt, model=model, validator=validator, optimizer=optimizer, repeat_count=repeat_count)