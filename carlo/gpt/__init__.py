import json
import openai
import project
from carlo import project
from carlo import printc
import time

openai.api_key = project.keys()["openai_key"]

def get_answer(prompt, model="gpt-3.5-turbo", temperature=1):
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
		return get_answer(prompt)
	return response.choices[0].message.content

def get_json(prompt, repeat_count=3):
	json_str = get_answer(prompt)
	try:
		json_data = json.loads(json_str)
		return json_data
	except json.JSONDecodeError as e:
		printc("Error decoding GPT JSON:", e)
		if repeat_count > 0:
			printc("Repeating GPT request...")
			return get_json(prompt, repeat_count=repeat_count-1)
		else:
			return None