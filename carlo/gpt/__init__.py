import json
import openai
from carlo import keychain
from carlo import printc
import time

openai.api_key = keychain.keys()["openai_key"]

def get_answer(prompt, model="gpt-3.5-turbo", temperature=1, validator=None, repeat_count=5):
	messages = [{"role": "user", "content": prompt}]
	try: 
		response = openai.ChatCompletion.create(
			model=model,
			messages=messages,
			temperature=temperature,
		)
	except openai.error.RateLimitError as e:
		retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
		printc(f"GPT rate limit exceeded. Retrying in {retry_time} seconds...")
		time.sleep(retry_time)
		return get_answer(prompt, model=model, temperature=temperature, validator=validator, repeat_count=repeat_count-1)
	except openai.error.OpenAIError as e:
		printc(f"Error from GPT: {e}")
		printc(f"Retrying in 30 seconds...")
		time.sleep(30)
		return get_answer(prompt, model=model, temperature=temperature, validator=validator, repeat_count=repeat_count-1)
	
	answer = response.choices[0].message.content
	if validator != None:
		if validator(answer):
			return answer
		elif repeat_count > 0:
			printc(f"Response didn't pass validation. Repeating GPT request...")
			return get_answer(prompt, model=model, temperature=temperature, validator=validator, repeat_count=repeat_count-1)
		else:
			return None
	else:
		return answer

def get_json(prompt, model="gpt-3.5-turbo", temperature=1, validator=None, repeat_count=5):
	prompt += "\nDon't add any extra text. Return only JSON."
	json_str = get_answer(prompt, model=model, temperature=temperature)
	try:
		json_data = json.loads(json_str)
		if validator != None:
			if validator(json_data):
				return json_data
			elif repeat_count > 0:
				printc(f"Response didn't pass validation. Repeating GPT request...")
				return get_json(prompt, model=model, temperature=temperature, validator=validator, repeat_count=repeat_count-1)
			else:
				return None
		else:
			return json_data
	except json.JSONDecodeError as e:
		printc(f"Error decoding GPT JSON: {e}")
		if repeat_count > 0:
			printc("Repeating GPT request...")
			return get_json(prompt, repeat_count=repeat_count-1, model=model, temperature=temperature)
		else:
			return None
		
def translate(text, target_language, model="gpt-3.5-turbo", note=""):
	prompt = f"Translate text into language {target_language}. {note}\nText: {text}\n Translation put in json with key 'translation'."
	output = get_json(prompt, model=model)
	if output == None:
		return None 
	if "translation" in output:
		return output["translation"]
	else:   
		return None