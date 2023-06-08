from carlo import project
from google.oauth2 import service_account
from googleapiclient.discovery import build

class Sheet:

	def insert_item(self, item, row=None):
		if row == None:
			row = 2 if len(self.items) == 0 else self.items[-1]["_row"] + 1
		item["_row"] = row
		for key, value in item.items():
			if key != "_row":
				self.set_item_value(item, value, key=key)
		return item

	def create_sheet(sheet_name, folder_id="", users=[]):
		# Replace the placeholders with your values
		credentials_file = project.keys()["google_credentials_path"]

		# Authenticate with Google Drive API using service account credentials
		credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])
		drive_service = build('drive', 'v3', credentials=credentials)

		# Create the Sheet in the folder
		sheet_metadata = {
			'name': sheet_name,
			'parents': [folder_id],
			'mimeType': 'application/vnd.google-apps.spreadsheet'
		}
		try:
			sheet = drive_service.files().create(body=sheet_metadata, fields='id').execute()
			sheet_id = sheet.get('id')
			sheet_link = sheet.get('webViewLink')
			print(f"Sheet '{sheet_name}' created with ID: {sheet_id}")
		except HttpError as error:
			print(f"An error occurred: {error}")
			exit()

		# Share the Sheet with users
		for user_email in users:
			permission_metadata = {
				'type': 'user',
				'role': 'writer',
				'emailAddress': user_email
			}
			try:
				permission = drive_service.permissions().create(
					fileId=sheet_id,
					body=permission_metadata,
					sendNotificationEmail=True).execute()
				print(f"Sheet '{sheet_name}' shared with user {user_email}")
			except HttpError as error:
				print(f"An error occurred: {error}")

		return sheet_id, sheet_link


	def command_center(page="dashboard"):
		return Sheet(project.keys()["command_center_sheet_id"], page=page)

	def __init__(self, sheet_id, page=""):
		self.sheet_id = sheet_id
		self.sheet_page = page
		self.refresh()

	def number_to_letter(self, num):
		letters = ''
		while num > 0:
			num -= 1
			letters = chr(num % 26 + 65) + letters
			num //= 26
		return letters

	def get_spreadsheets():
		scopes = ['https://www.googleapis.com/auth/spreadsheets']
		creds = service_account.Credentials.from_service_account_file(project.keys()["google_credentials_path"], scopes=scopes)
		service = build('sheets', 'v4', credentials=creds)
		return service.spreadsheets()

	def get_items(self):
		result = self.spreadsheets.values().get(spreadsheetId=self.sheet_id, range=f'{self.sheet_page}!A1:CZ100000').execute()
		values = result.get('values', [])
		items = []
		fields = list(filter(lambda f: len(f) > 0, values[0]))
		for i in range(1, len(values)):
			item = {'_row': i + 1}
			for j in range(len(fields)):
				item[fields[j]] = values[i][j] if j < len(values[i]) else ''

			items.append(item)
		return items, fields

	def set_fields(self, fields):
		self.set_values(fields, row=1)		

	def set_values(self, values, row=1):
		column = self.number_to_letter(len(values))
		sheet_range = f'{self.sheet_page}!A{row}:{column}{row}'
		body = {
			'range': sheet_range,
			'values': [values],
			'majorDimension': 'ROWS'
		}
		result = self.spreadsheets.values().update(
			spreadsheetId=self.sheet_id, 
			range=sheet_range, 
			valueInputOption='USER_ENTERED', 
			body=body
		).execute()

	def set_item_value(self, item, value, key=None):
		item[key] = value
		column = self.number_to_letter(self.fields.index(key) + 1)
		sheet_range = f'{self.sheet_page}!{column}{item["_row"]}'
		body = {
			'range': sheet_range,
			'values': [[value]],
			'majorDimension': 'ROWS'
		}
		result = self.spreadsheets.values().update(
			spreadsheetId=self.sheet_id, 
			range=sheet_range, 
			valueInputOption='USER_ENTERED', 
			body=body
		).execute()

	def refresh(self):
		self.items, self.fields = self.get_items()

	sheet_id = ""
	sheet_page = ""
	spreadsheets = get_spreadsheets()
	items = []
	fields = []

