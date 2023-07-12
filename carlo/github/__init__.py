import requests
import json
from carlo import keychain

def repository_exists(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    access_token = keychain.keys()["github_access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"{url} repository exists.")
        return True
    elif response.status_code == 404:
        return False
    else:
        return False

def create_repo(repo_name, collaborators):
    # Replace <username> with your GitHub username
    username = keychain.keys()["github_username"]
    # Replace <access_token> with your GitHub personal access token
    access_token = keychain.keys()["github_access_token"]

    # Set the API endpoint
    org_name = keychain.keys()["github_organization"]
    
    if repository_exists(org_name, repo_name):
        return f"https://github.com/{org_name}/{repo_name}.git"
    

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
        print(f"https://github.com/{org_name}/{repo_name}.git")
        print(f'An error occurred: {response.text}')
        return None