from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
from carlo import keychain

credentials_file = keychain.keys()["google_credentials_path"]
credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=["https://www.googleapis.com/auth/drive"])
drive_service = build("drive", "v3", credentials=credentials)

def get_folder_name(folder_id):
	try:
		# Call the Drive API
		folder = drive_service.files().get(fileId=folder_id, fields='name').execute()
		print(f"The name of the folder is: {folder['name']}")
	except TypeError as error:
		print(f"An error occurred: {error}")
	return folder['name']

def get_folder_url(folder_id):
	return f"https://drive.google.com/drive/folders/{folder_id}"

def create_folder(folder_name, parent_folder_id=None, users=[]):
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
	except TypeError as error:
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
				sendNotificationEmail=False).execute()
			print(f"Folder '{folder_name}' shared with user {user_email}")
		except TypeError as error:
			print(f"An error occurred: {error}")

	return folder_id

def get_folder_id(relative_path, parent_folder_id=""):
	# Set the query parameter to retrieve only folders contained in the parent folder
    folder_id = parent_folder_id

    # Split the relative path into individual folder names
    folders = relative_path.split('/')

    for folder_name in folders:
        # Search for the folder within the current folder ID
        query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}'"
        response = drive_service.files().list(q=query).execute()

        # Check if the folder exists
        folders_in_drive = response.get('files', [])
        if len(folders_in_drive) > 0:
            folder_id = folders_in_drive[0]['id']
        else:
            return None  # Folder not found

    return folder_id

def upload_file(file_path, folder_id, mimetype='image/png'):
	# Upload the image to the specified folder
	file_metadata = {'name': file_path.split("/")[-1], 'parents': [folder_id]}
	media = MediaFileUpload(file_path, mimetype=mimetype)
	file = drive_service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()

	# Get the ID and public link of the uploaded file
	file_id = file.get('id')
	public_link = file.get('webViewLink')

	return file_id, public_link

def folder_contents(folder_id):
	# Get the contents of the folder
	query = f"'{folder_id}' in parents"
	response = drive_service.files().list(q=query).execute()
	return response.get('files', [])

def folder_contains_file(folder_id, file_name):
	# Search for the file in the folder
	query = f"'{folder_id}' in parents and name = '{file_name}'"
	response = drive_service.files().list(q=query).execute()
	files = response.get('files', [])
	if files:
		return True
	else:
		return False

def delete_folder(folder_id):
	try:
		drive_service.files().delete(fileId=folder_id).execute()
		print(f"Folder with ID '{folder_id}' deleted successfully.")
	except TypeError as error:
		print(f"An error occurred: {error}")


