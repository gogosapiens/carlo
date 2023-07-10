import requests
import json
from carlo.keys import keys

def create_repo(repo_name, collaborators):
    # Replace <username> with your GitHub username
    username = keys()["github_username"]
    # Replace <access_token> with your GitHub personal access token
    access_token = keys()["github_access_token"]

    # Set the API endpoint
    org_name = keys()["github_organization"]
    url = f'https://api.github.com/orgs/{org_name}/repos'

    # Set the request headers and payload
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'token {access_token}'
    }
    payload = {'name': repo_name, 'private': True, 'collaborators': collaborators}

    # Send the POST request to create the repository
    response = requests.post(url, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 201:
        print('Repository created successfully.')
        return f"https://github.com/{org_name}/{repo_name}.git"
    else:
        print(f'An error occurred: {response.text}')
        return None