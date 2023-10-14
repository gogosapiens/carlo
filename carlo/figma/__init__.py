import requests
from carlo import keychain, printc

class Figma:
    
    def __init__(self, file_key):
        self.file_key = file_key

    def export_node(self, node_id, output_image, scale=1):
        # Set the Figma API endpoint and access token
        api_url = 'https://api.figma.com/v1'

        access_token = keychain.keys()["figma_access_token"]

        # Construct the Figma API URL for the text layer
        url = f'{api_url}/images/{self.file_key}?ids={node_id}&format=png&scale={scale}'

        # Make a GET request to the Figma API to get the current text style of the text layer
        headers = {'X-Figma-Token': access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(response.json())
            image_url = response.json()["images"][node_id]
            print(image_url)
            response = requests.get(image_url)
            print(response)
            with open(output_image, 'wb') as f:
                f.write(response.content)
            return True
        else:
            return False

