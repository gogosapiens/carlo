from carlo import printc
from carlo import gpt

def validate_resp(response):
    # print("validating response", response)
    response['title'] = "value1"
    return True
    
def optimizer_resp(response):
    # print("optimizing response", response)
    # if isinstance(response, str):
    #     return "value222"
    # else:
    return 1

response = gpt.get_json("Return json with structure {'title': 'fsdfds', 'subtitle': 'fdsfds'}", validator=validate_resp, optimizer=optimizer_resp, repeat_count=3)
print(response)