import requests
from carlo import keychain

class Asana:
    workspace_gid = ""
    api_token = keychain.keys()["asana_access_token"]

    def __init__(self, workspace_gid):
        self.workspace_gid = workspace_gid

    def create_project(self, project_name, project_description=""):
        url = f"https://app.asana.com/api/1.0/workspaces/{self.workspace_gid}/projects"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        data = {
            "data": {
                "name": project_name,
                "notes": project_description
            }
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code // 100 == 2:
            project_data = response.json()
            project_gid = project_data["data"]["gid"]
            print(f"Project created! GID: {project_gid}")
            return AsanaProject(project_gid, self.workspace_gid)
        else:
            print(f"Error creating project: {response.text}")
            return None

    def get_user_gid(self, email):
        url = "https://app.asana.com/api/1.0/users"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        params = {"data": {"opt_fields": "gid", "email": email} }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            users_data = response.json()
            if users_data["data"]:
                user_gid = users_data["data"][0]["gid"]
                print(f"User with email '{email}' found! GID: {user_gid}")
                return user_gid
            else:
                print(f"User with email '{email}' not found.")
                return None
        else:
            print(f"Error retrieving user data: {response.text}")
            return None
        
        
class AsanaProject:
    asana = None
    project_gid = ""

    def __init__(self, project_gid, workspace_gid):
        self.project_gid = project_gid
        self.asana = Asana(workspace_gid)

    def url(self):
        return f"https://app.asana.com/0/{self.project_gid}"
    
    def invite_users(self, email_list):
        url = f"https://app.asana.com/api/1.0/projects/{self.project_gid}/addMembers"
        headers = {"Authorization": f"Bearer {self.asana.api_token}"}
        data = {"data": {"members": [{"email": email} for email in email_list]} } # Convert email_list to list of dictionaries

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("Users invited to the project successfully!")
            return True
        else:
            print(f"Error inviting users to the project: {response.text}")
            return False


    def create_section(self, section_name):
        url = f"https://app.asana.com/api/1.0/projects/{self.project_gid}/sections"
        headers = {"Authorization": f"Bearer {self.asana.api_token}"}
        data = {"data": {"name": section_name} }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            section_data = response.json()
            section_gid = section_data["data"]["gid"]
            print(f"Section created! GID: {section_gid}")
            return section_gid
        else:
            print(f"Error creating section: {response.text}")
            return None
    
    def get_section_id(self, section_name):
        url = f"https://app.asana.com/api/1.0/projects/{self.project_gid}/sections"
        headers = {"Authorization": f"Bearer {self.asana.api_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            sections_data = response.json()
            for section in sections_data["data"]:
                if section["name"] == section_name:
                    section_gid = section["gid"]
                    print(f"Section '{section_name}' found! GID: {section_gid}")
                    return section_gid

            print(f"Section '{section_name}' not found.")
            return None
        else:
            print(f"Error retrieving sections: {response.text}")
            return None

    def create_task(self, section_gid, task_name, task_description=None):
        url = f"https://app.asana.com/api/1.0/sections/{section_gid}/tasks"
        headers = {"Authorization": f"Bearer {self.asana.api_token}"}
        data = {
            "data": {
                "name": task_name,
                "notes": task_description
            }
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 201:
            task_data = response.json()
            task_gid = task_data["data"]["gid"]
            print(f"Task created! GID: {task_gid}")
            return task_gid
        else:
            print(f"Error creating task: {response.text}")
            return None
        
    def get_task(self, section_gid, task_name, parent_task_id=None):
        url = f"https://app.asana.com/api/1.0/sections/{section_gid}/tasks"
        headers = {"Authorization": f"Bearer {self.asana.api_token}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tasks_data = response.json()
            for task in tasks_data["data"]:
                if task["name"] == task_name:
                    if parent_task_id:
                        if "parent" in task and task["parent"]["gid"] == parent_task_id:
                            task_gid = task["gid"]
                            print(f"Task '{task_name}' found! GID: {task_gid}")
                            return AsanaTask(self, section_gid, task_gid)
                    else:
                        task_gid = task["gid"]
                        print(f"Task '{task_name}' found! GID: {task_gid}")
                        return AsanaTask(self, section_gid, task_gid)

            print(f"Task '{task_name}' not found in the specified section.")
            return None
        else:
            print(f"Error retrieving tasks: {response.text}")
            return None
        
class AsanaTask:
    project = None
    section_gid = ""
    task_gid = ""

    def __init__(self, project, section_gid, task_gid):
        self.project = project
        self.section_gid = section_gid
        self.task_gid = task_gid

    def add_child(self, child_task):
        url = f"https://app.asana.com/api/1.0/tasks/{child_task.task_gid}/setParent"
        headers = {"Authorization": f"Bearer {self.project.asana.api_token}"}
        data = {"parent": self.task_gid}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"Task {child_task.task_gid} set as a subtask of {self.task_gid}.")
            return True
        else:
            print(f"Error setting task as a subtask: {response.text}")
            return False
        
    

    