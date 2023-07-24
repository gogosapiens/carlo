import requests
import json
from carlo import keychain
import subprocess
import os

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
    
def checkout_repo(repo_url, local_folder):
    try:
        # Clone the repository to the specified destination path
        subprocess.run(['git', 'clone', repo_url, local_folder])
        print("Repository cloned successfully.")
    except Exception as e:
        print(f"Error: {e}")


def commit_and_push_repo(local_folder, commit_message="Update"):
    original_cwd = os.getcwd()
    os.chdir(local_folder)
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', commit_message])
    subprocess.run(['git', 'push', 'origin', 'main'])
    os.chdir(original_cwd)


def duplicate_repo(source_url, destination_url):
    try:
        # Step 1: Clone the source repository
        subprocess.run(['git', 'clone', '--mirror', source_url])

        # Step 2: Get the name of the source repository
        source_repo_name = source_url.split('/')[-1].replace('.git', '')

        # Step 3: Change into the cloned repository directory
        cloned_repo_path = f"./{source_repo_name}.git"
        os.chdir(cloned_repo_path)

        # Step 4: Check if the "destination" remote already exists
        existing_remote_check = subprocess.run(['git', 'remote'], capture_output=True, text=True)
        if 'destination' in existing_remote_check.stdout:
            # Remove the existing "destination" remote
            subprocess.run(['git', 'remote', 'remove', 'destination'])

        # Step 5: Add the destination remote repository
        subprocess.run(['git', 'remote', 'add', 'destination', destination_url])

        # Step 6: Push all branches and tags to the destination remote
        process = subprocess.Popen(['git', 'push', '--mirror', 'destination'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Print any output from the Git push process
        if stdout:
            print(stdout.decode('utf-8'))
        if stderr:
            print(stderr.decode('utf-8'))

        # Step 7: Change back to the original working directory
        os.chdir('..')

        # Step 8: Clean up the cloned repository (optional)
        subprocess.run(['rm', '-rf', cloned_repo_path])

        print("Repository copied successfully!")
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
