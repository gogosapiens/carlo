from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from carlo import project

credentials_file = project.keys()["google_credentials_path"]
credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=["https://www.googleapis.com/auth/drive"])
drive_service = build("drive", "v3", credentials=credentials)

def get_folder_name(folder_id):
	try:
		# Call the Drive API
		folder = drive_service.files().get(fileId=folder_id, fields='name').execute()
		print(f"The name of the folder is: {folder['name']}")
	except HttpError as error:
		print(f"An error occurred: {error}")
	return folder['name']

def create_folder(folder_name, parent_folder_id=None, users=project.keys()["google_drive_users"]):
	# Create the folder
	folder_metadata = {
		'name': folder_name,
		'mimeType': 'application/vnd.google-apps.folder',
		'parents': [] if parent_folder_id == None else [parent_folder_id]
	}
	try:
		folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
		folder_id = folder.get('id')
		print(f"Folder '{folder_name}' created with ID: {folder_id}")
	except HttpError as error:
		print(f"An error occurred: {error}")
		exit()

	# Share the folder with users
	for user_email in users:
		permission_metadata = {
			'type': 'user',
			'role': 'writer',
			'emailAddress': user_email
		}
		try:
			permission = drive_service.permissions().create(
				fileId=folder_id,
				body=permission_metadata,
				sendNotificationEmail=True).execute()
			print(f"Folder '{folder_name}' shared with user {user_email}")
		except HttpError as error:
			print(f"An error occurred: {error}")

	return folder_id


def get_folder_id(folder_name, parent_folder_id=""):
	# Set the query parameter to retrieve only folders contained in the parent folder
	query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
	try:
		# Call the Drive API
		results = drive_service.files().list(q=query, fields='files(id, name)').execute()

		# Check if any of the folders in the results list has the same name as the folder we are looking for
		for item in results['files']:
			if item['name'] == folder_name:
				return item['id']

		# The folder was not found inside the parent folder
		return None

	except HttpError as error:
		print(f"An error occurred: {error}")
		return None


def delete_folder(folder_id):
	try:
		drive_service.files().delete(fileId=folder_id).execute()
		print(f"Folder with ID '{folder_id}' deleted successfully.")
	except HttpError as error:
		print(f"An error occurred: {error}")

