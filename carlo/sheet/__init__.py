from carlo.keys import keys
from google.oauth2 import service_account
from googleapiclient.discovery import build

class Sheet:

	def insert_item(self, new_item, row=None):
		if row == None:
			row = 2 if len(self.items) == 0 else self.items[-1]["_row"] + 1
		keyValues = new_item.copy()
		new_item["_row"] = row
		self.set_item_values(new_item, keyValues)
		return new_item


	def insert_items(self, new_items, row=None):
		if row == None:
			row = 2 if len(self.items) == 0 else self.items[-1]["_row"] + 1
		for index, new_item in enumerate(new_items):
			keyValues = new_item.copy()
			new_item["_row"] = row + index
			self.set_item_values(new_item, keyValues)
		return new_items

	@classmethod
	def duplicate_sheet(new_sheet_name, template_sheet_id="", folder_id="", users=[]):
		credentials_file = keys()["google_credentials_path"]
		credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])

		sheets_service = build('sheets', 'v4', credentials=credentials)
		drive_service = build('drive', 'v3', credentials=credentials)

		# ID of the source sheet to be duplicated
		source_sheet_id = template_sheet_id

		# Folder ID where the duplicated sheet will be placed
		destination_folder_id = folder_id

		duplicated_sheet_name = new_sheet_name

		# Email addresses of users to provide edit permissions
		user_emails = users

		# Duplicate the sheet
		duplicate_request = sheets_service.spreadsheets().sheets().copyTo(spreadsheetId=source_sheet_id,
																		sheetId=0)
		duplicate_response = duplicate_request.execute()
		duplicated_sheet_id = duplicate_response['sheetId']

		# Rename the duplicated sheet
		request = sheets_service.spreadsheets().batchUpdate(spreadsheetId=duplicated_sheet_id, body={
			'requests': [{'updateSheetProperties': {'properties': {'sheetId': 0, 'title': duplicated_sheet_name}, 'fields': 'title'}}]
		})
		request.execute()

		# Move the duplicated sheet to the specified folder
		drive_service.files().update(fileId=duplicated_sheet_id,
									addParents=destination_folder_id,
									removeParents='root').execute()

		# Share the duplicated sheet with users for edit access
		for email in user_emails:
			permission = {
				'type': 'user',
				'role': 'writer',
				'emailAddress': email
			}
			drive_service.permissions().create(fileId=duplicated_sheet_id, body=permission).execute()

		# Get the web link and new sheet ID
		response = drive_service.files().get(fileId=duplicated_sheet_id,
											fields='webViewLink').execute()
		web_link = response['webViewLink']
		
		return duplicated_sheet_id, web_link
		

	@classmethod
	def create_sheet(sheet_name, folder_id="", users=[]):
		# Replace the placeholders with your values
		credentials_file = keys()["google_credentials_path"]

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
		except TypeError as error:
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
			except TypeError as error:
				print(f"An error occurred: {error}")

		return sheet_id, sheet_link


	def projects_sheet(page="projects"):
		return Sheet(keys()["projects_sheet_id"], page=page)
	
	def get_item(self, condition):
		items = list(filter(condition, self.items))
		return items[0] if len(items) > 0 else None

	def app_sheet(app_id, page="texts"):
		projects_sheet = Sheet.projects_sheet()
		project_app_items = list(filter(lambda item: item["app_id"] == app_id, projects_sheet.items))
		project_app_item = project_app_items[0] if len(project_app_items) > 0 else None
		app_sheet_id = project_app_item["app_sheet_url"].split("/")[-1]
		return Sheet(app_sheet_id, page=page)


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
		creds = service_account.Credentials.from_service_account_file(keys()["google_credentials_path"], scopes=scopes)
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


	def divide_list(self, numbers):
		result = []
		sublist = []
		for i in range(len(numbers)):
			sublist.append(numbers[i])
			if i + 1 < len(numbers) and numbers[i + 1] != numbers[i] + 1:
				result.append(sublist)
				sublist = []
		if sublist:
			result.append(sublist)
		return result


	def set_item_values(self, task, keyValues):
		key_indexes = sorted(list(map(lambda key: self.fields.index(key) + 1, keyValues.keys())))
		groups = self.divide_list(key_indexes)
		for group in groups:
			column1 = self.number_to_letter(group[0])
			column2 = self.number_to_letter(group[-1])
			sheet_range = f'{self.sheet_page}!{column1}{task["_row"]}:{column2}{task["_row"]}'
			values = list(map(lambda index: keyValues[self.fields[index - 1]], group))
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
		for key in keyValues.keys():
			task[key] = keyValues[key]


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

