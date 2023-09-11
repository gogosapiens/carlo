import json
import openai
import requests
from carlo import keychain
from carlo import printc
import time
import concurrent.futures

openai.api_key = keychain.keys()["openai_key"]
DEFAULT_MODEL = "gpt-3.5-turbo"
REQUEST_TIMEOUT = 30

def get_text(prompt, model=DEFAULT_MODEL, temperature=1, validator=None, optimizer=None, ranks=None, repeat_count=10):
	if ranks is None:
		ranks = []
	messages = [{"role": "user", "content": prompt}]

	def request():
		try:
			response = openai.ChatCompletion.create(
				model=model,
				messages=messages,
				temperature=temperature,
			)
			return response.choices[0].message.content
		except openai.error.RateLimitError as e:
			retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
			printc(f"GPT rate limit exceeded. Retrying in {retry_time} seconds...")
			time.sleep(retry_time)
			return None
		except openai.error.OpenAIError as e:
			printc(f"Error from GPT: {e}")
			printc(f"Retrying in 30 seconds...")
			time.sleep(30)
			return None
		except requests.exceptions.Timeout:
			printc("GPT request timed out. Retrying in 30 seconds...")
			time.sleep(30)
			return None
		except Exception as e:
			printc(f"Unexpected GPT error occurred: {e}")
			return None

	with concurrent.futures.ThreadPoolExecutor() as executor:
		future = executor.submit(request)
		try:
			answer = future.result(timeout=REQUEST_TIMEOUT)
		except concurrent.futures.TimeoutError:
			printc(f"GPT request exceeded {REQUEST_TIMEOUT} seconds. Canceling and retrying...")
			future.cancel()
			return get_text(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
		
	if validator != None:
		if validator(answer):
			return get_text_optimizer_logic(answer, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count)
		else:
			if repeat_count > 0:
				printc(f"Response didn't pass validation. Repeating GPT request...")
				return get_text(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
			else:
				return best_results(ranks)
	else:
		return get_text_optimizer_logic(answer, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count)


def get_text_optimizer_logic(response, prompt, model, temperature, validator, optimizer, ranks, repeat_count):
	if optimizer != None:
		rank = optimizer(response)
		ranks.append((response, rank))
		if repeat_count > 0:
			printc(f"Optimizing score: {rank}. Repeating GPT request...")
			return get_text(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
		else:
			return best_results(ranks)
	else:
		return response
	
def get_json_optimizer_logic(response, prompt, model, temperature, validator, optimizer, ranks, repeat_count):
	if optimizer != None:
		rank = optimizer(response)
		ranks.append((response, rank))
		if repeat_count > 0:
			printc(f"Optimizing score: {rank}. Repeating GPT request...")
			return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
		else:
			return best_results(ranks)
	else:
		return response

def get_value(prompt, model=DEFAULT_MODEL, temperature=1, validator=None, optimizer=None, repeat_count=10):
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

	result = get_json(prompt, model=model, temperature=temperature, validator=validator_func, optimizer=optimizer_func, ranks=[], repeat_count=repeat_count)
	if result != None:
		return result[key]
	else:
		return None

def best_results(ranks):
	if len(ranks) > 0:
		ranks.sort(key=lambda x: x[1], reverse=True)
		return ranks
	else:
		return None

def get_json(prompt, model=DEFAULT_MODEL, temperature=1, validator=None, optimizer=None, ranks=None, repeat_count=10):
	if ranks is None:
		ranks = []
	prompt += "\nDon't add any extra text. Return only JSON."
	json_str = get_text(prompt, model=model, temperature=temperature, repeat_count=repeat_count)
	try:
		json_data = json.loads(json_str)
		if validator != None:
			if validator(json_data):
				return get_json_optimizer_logic(json_data, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count)
			else:
				if repeat_count > 0:
					printc(f"Response didn't pass validation. Repeating GPT request...")
					return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
				else:
					return best_results(ranks)
		else:
			return get_json_optimizer_logic(json_data, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count)

	except json.JSONDecodeError as e:
		if repeat_count > 0:
			printc(f"Error decoding GPT JSON: {e}")
			printc("Repeating GPT request...")
			return get_json(prompt, model=model, temperature=temperature, validator=validator, optimizer=optimizer, ranks=ranks.copy(), repeat_count=repeat_count-1)
		else:
			printc(f"Error decoding GPT JSON: {e}")
			return get_json_optimizer_logic(json_data, prompt, model, temperature, validator, optimizer, ranks.copy(), repeat_count)
		
def translate(text, target_language, model=DEFAULT_MODEL, note="", validator=None, optimizer=None, repeat_count=10):
	prompt = f"Translate text into language {target_language}. {note}\nText: {text}\n"
	return get_value(prompt, model=model, validator=validator, optimizer=optimizer, repeat_count=repeat_count)