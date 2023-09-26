from carlo import printc
from carlo import gpt

def validate_resp(response):
    # print("validating response", response)
    # if isinstance(response, str):
    #     return "value222"
    # else:
    return True
    
response = gpt.get_json("Return capital of USA", validator=validate_resp, repeat_count=10)
print(response)