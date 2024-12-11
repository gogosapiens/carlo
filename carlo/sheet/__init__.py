from carlo import keychain
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

class Sheet:

	def url(self):
		return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

	def insert_item(self, new_item, row=None):
		if row == None:
			row = 2 if len(self.items) == 0 else self.items[-1]["_row"] + 1
		key_values = new_item.copy()
		new_item["_row"] = row
		self.set_item_values(new_item, key_values)
		return new_item

	def insert_items(self, new_items, row=None):
		if row == None:
			row = 2 if len(self.items) == 0 else self.items[-1]["_row"] + 1
		item_values_tuples = []
		for index, new_item in enumerate(new_items):
			key_values = new_item.copy()
			new_item["_row"] = row + index
			item_values_tuples.append((new_item, key_values))
		self.set_items_values(item_values_tuples)
		return new_items

	def duplicate_sheet(new_sheet_name, template_sheet_id="", folder_id="", users=[]):
		credentials_file = keychain.keys()["google_credentials_path"]
		credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])

		drive_service = build('drive', 'v3', credentials=credentials)

		# Make a copy of the original spreadsheet
		copied_file = {'name': new_sheet_name}
		request = drive_service.files().copy(fileId=template_sheet_id, body=copied_file, fields='id, parents')
		file = request.execute()
		# Move the copied spreadsheet to the desired folder
		file_id = file['id']
		request = drive_service.files().update(
			fileId=file_id,
			addParents=folder_id,
			removeParents=file['parents'][0],
			fields='id, parents'
		)
		file = request.execute()

		# Share the copied spreadsheet with desired users
		batch = drive_service.new_batch_http_request()
		user_permission = {
			'type': 'user',
			'role': 'writer'
		}
		for email in users:
			user_permission['emailAddress'] = email
			batch.add(drive_service.permissions().create(
				fileId=file_id,
				body=user_permission,
				fields='id',
			))
		batch.execute()

		# Get the spreadsheet ID and URL
		spreadsheet_id = file['id']
		spreadsheet_url = 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id

		return spreadsheet_id, spreadsheet_url
		
	def clear(self):
		column = self.number_to_letter(len(self.fields))
		sheet_range = f'{self.sheet_page}!A2:{column}{len(self.items) + 1}'
		empty_row = [''] * len(self.fields)
		empty_table = [empty_row] * len(self.items)
		body = {
			'range': sheet_range,
			'values': empty_table,
			'majorDimension': 'ROWS'
		}
		self.perform_update_sheet_action(sheet_range, body)
		self.refresh()
		

	def create_sheet(sheet_name, folder_id="", users=[]):
		# Replace the placeholders with your values
		credentials_file = keychain.keys()["google_credentials_path"]

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

		return sheet_id, 'https://docs.google.com/spreadsheets/d/' + sheet_id

	
	def get_item(self, condition):
		items = list(filter(condition, self.items))
		return items[0] if len(items) > 0 else None

	def __init__(self, sheet_id, page=""):
		self.spreadsheets = self.get_spreadsheets()
		self.items = []
		self.fields = []
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

	def get_spreadsheets(self):
		scopes = ['https://www.googleapis.com/auth/spreadsheets']
		creds = service_account.Credentials.from_service_account_file(keychain.keys()["google_credentials_path"], scopes=scopes)
		service = build('sheets', 'v4', credentials=creds)
		return service.spreadsheets()

	max_range = "A1:CZ100000"

	def get_items(self):
		result = self.perform_get_sheet_action(f'{self.sheet_page}!{Sheet.max_range}')
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
		self.perform_update_sheet_action(sheet_range, body)


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
	
	def divide_list_verticaly(self, item_value_tuples):
		result = []
		sublist = []
		item_value_tuples = sorted(item_value_tuples, key=lambda item_value_tuple: item_value_tuple[0]["_row"])
		for i in range(len(item_value_tuples)):
			sublist.append(item_value_tuples[i])
			if i + 1 < len(item_value_tuples) and item_value_tuples[i + 1][0]["_row"] != item_value_tuples[i][0]["_row"] + 1:
				indexes = range(i - len(sublist) + 1, i + 1)
				result_item = list(map(lambda index: (item_value_tuples[index][0], item_value_tuples[index][1]), indexes))
				result.append(result_item)
				sublist = []
		if sublist:
			indexes = range(len(item_value_tuples) - len(sublist), len(item_value_tuples))
			result_item = list(map(lambda index: (item_value_tuples[index][0], item_value_tuples[index][1]), indexes))
			result.append(result_item)
		return result

	def set_item_values(self, item, key_values):
		key_indexes = sorted(list(map(lambda key: self.fields.index(key) + 1, key_values.keys())))
		groups = self.divide_list(key_indexes)
		for group in groups:
			column1 = self.number_to_letter(group[0])
			column2 = self.number_to_letter(group[-1])
			sheet_range = f'{self.sheet_page}!{column1}{item["_row"]}:{column2}{item["_row"]}'
			values = list(map(lambda index: key_values[self.fields[index - 1]], group))
			body = {
				'range': sheet_range,
				'values': [values],
				'majorDimension': 'ROWS'
			}
			self.perform_update_sheet_action(sheet_range, body)
		for key in key_values.keys():
			item[key] = key_values[key]

	def set_straight_items_values(self, item_value_tuples):
		key_values = item_value_tuples[0][1]
		key_indexes = sorted(list(map(lambda key: self.fields.index(key) + 1, key_values.keys())))
		groups = self.divide_list(key_indexes)
		for group in groups:
			column1 = self.number_to_letter(group[0])
			column2 = self.number_to_letter(group[-1])
			sheet_range = f'{self.sheet_page}!{column1}{item_value_tuples[0][0]["_row"]}:{column2}{item_value_tuples[-1][0]["_row"]}'
			values = []
			for item_value_tuple in item_value_tuples:
				values.append(list(map(lambda index: item_value_tuple[1][self.fields[index - 1]], group)))
			body = {
				'range': sheet_range,
				'values': values,
				'majorDimension': 'ROWS'
			}
			self.perform_update_sheet_action(sheet_range, body)
		for item_value_tuple in item_value_tuples:
			for key in item_value_tuple[1].keys():
				item_value_tuple[0][key] = item_value_tuple[1][key]


	def set_items_values(self, item_value_tuples):
		groups = self.divide_list_verticaly(item_value_tuples)
		for group in groups:
			self.set_straight_items_values(group)

	def set_item_value(self, item, value, key=None):
		item[key] = value
		column = self.number_to_letter(self.fields.index(key) + 1)
		sheet_range = f'{self.sheet_page}!{column}{item["_row"]}'
		body = {
			'range': sheet_range,
			'values': [[value]],
			'majorDimension': 'ROWS'
		}
		self.perform_update_sheet_action(sheet_range, body)


	def perform_get_sheet_action(self, range):
		try:
			return self.spreadsheets.values().get(spreadsheetId=self.sheet_id, range=range).execute()
		except HttpError as e:
			if e.resp.status == 429:
				# Quota exceeded, handle this error
				print("Spreadsheets quota exceeded. Waiting for 60 seconds before retrying...")
				time.sleep(60)
				# Retry the operation after waiting
				return self.perform_get_sheet_action(range)
			else:
				# Handle other HTTP errors here
				print(f"An HTTP error occurred: {e}")
				print("Sleeping for 10 seconds before retrying...")
				time.sleep(10)
				return self.perform_get_sheet_action(range)
		except Exception as e:
			# Handle other exceptions here
			print(f"An error occurred: {e}")
			return None


	def perform_update_sheet_action(self, range, body):
		try:
			result = self.spreadsheets.values().update(
				spreadsheetId=self.sheet_id, 
				range=range, 
				valueInputOption='USER_ENTERED', 
				body=body
			).execute()
		except HttpError as e:
			if e.resp.status == 429:
				# Quota exceeded, handle this error
				print("Spreadsheets quota exceeded. Waiting for 60 seconds before retrying...")
				time.sleep(60)
				# Retry the operation after waiting
				self.perform_update_sheet_action(range, body)
			else:
				# Handle other HTTP errors here
				print(f"An HTTP error occurred: {e}")
				print("Sleeping for 10 seconds before retrying...")
				time.sleep(10)
				self.perform_update_sheet_action(range, body)
		except Exception as e:
			# Handle other exceptions here
			print(f"An error occurred: {e}")

	def refresh(self):
		self.items, self.fields = self.get_items()


######################################################


class HorizontalSheet:

	MAX_RANGE = "A1:CZ100000"

	def insert_item(self, new_item, column=None): # fixed
		if column == None:
			column = "B" if len(self.items) == 0 else self.number_to_letter(len(self.items) + 2)
		key_values = new_item.copy()
		new_item["_column"] = column
		self.set_item_values(new_item, key_values)
		return new_item

	def insert_items(self, new_items, column=None): # fixed
		if column == None:
			column = "B" if len(self.items) == 0 else self.number_to_letter(len(self.items) + 2)
		column_number = self.letter_to_number(column)
		item_values_tuples = []
		for index, new_item in enumerate(new_items):
			key_values = new_item.copy()
			new_item["_column"] = self.number_to_letter(column_number + index)
			item_values_tuples.append((new_item, key_values))
		self.set_items_values(item_values_tuples)
		return new_items
		
	def clear(self): # fixed
		column = self.number_to_letter(len(self.items) + 1)
		sheet_range = f'{self.sheet_page}!B1:{column}{len(self.fields)}'
		empty_row = [''] * len(self.items)
		empty_table = [empty_row] * len(self.fields)
		body = {
			'range': sheet_range,
			'values': empty_table,
			'majorDimension': 'ROWS'
		}
		self.perform_update_sheet_action(sheet_range, body)
		self.refresh()

	def __init__(self, sheet_id, page=""): # fixed
		self.spreadsheets = self.get_spreadsheets()
		self.items = []
		self.fields = []
		self.sheet_id = sheet_id
		self.sheet_page = page
		self.refresh()

	def number_to_letter(self, num): # fixed
		letters = ''
		while num > 0:
			num -= 1
			letters = chr(num % 26 + 65) + letters
			num //= 26
		return letters
	
	def letter_to_number(self, letter): # fixed
		number = 0
		for i in range(len(letter)):
			number = number * 26 + ord(letter[i]) - 64
		return number

	def get_spreadsheets(self): # fixed
		scopes = ['https://www.googleapis.com/auth/spreadsheets']
		creds = service_account.Credentials.from_service_account_file(keychain.keys()["google_credentials_path"], scopes=scopes)
		service = build('sheets', 'v4', credentials=creds)
		return service.spreadsheets()

	def get_items(self): # fixed
		result = self.perform_get_sheet_action(f'{self.sheet_page}!{HorizontalSheet.MAX_RANGE}')
		values = result.get('values', [])
		items = []
		fields = list(map(lambda f: f[0], filter(lambda f: len(f) > 0, values)))
		# find max length of values
		max_length = 0
		for i in range(1, len(values)):
			max_length = max(max_length, len(values[i]))
		for i in range(1, max_length):
			item = {'_column': self.number_to_letter(i + 1)}
			for j in range(len(fields)):
				item[fields[j]] = values[j][i] if i < len(values[j]) else ''
			items.append(item)
		return items, fields

	def set_fields(self, fields): # fixed
		column = "A"
		row_1 = 1
		row_2 = len(fields)
		sheet_range = f'{self.sheet_page}!{column}{row_1}:{column}{row_2}'
		vertical_fields = [[field] for field in fields]
		body = {
			'range': sheet_range,
			'values': vertical_fields,
			'majorDimension': 'ROWS'
		}
		self.perform_update_sheet_action(sheet_range, body)		

	def divide_list(self, numbers): # fixed
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
	
	def divide_list_verticaly(self, item_value_tuples): # fixed
		result = []
		sublist = []
		item_value_tuples = sorted(item_value_tuples, key=lambda item_value_tuple: self.letter_to_number(item_value_tuple[0]["_column"]))
		for i in range(len(item_value_tuples)):
			sublist.append(item_value_tuples[i])
			if i + 1 >= len(item_value_tuples):
				break
			column_number_1 = self.letter_to_number(item_value_tuples[i][0]["_column"])
			column_number_2 = self.letter_to_number(item_value_tuples[i + 1][0]["_column"])
			if column_number_2 != column_number_1 + 1:
				indexes = range(i - len(sublist) + 1, i + 1)
				result_item = list(map(lambda index: (item_value_tuples[index][0], item_value_tuples[index][1]), indexes))
				result.append(result_item)
				sublist = []
		if sublist:
			indexes = range(len(item_value_tuples) - len(sublist), len(item_value_tuples))
			result_item = list(map(lambda index: (item_value_tuples[index][0], item_value_tuples[index][1]), indexes))
			result.append(result_item)
		return result

	def set_item_values(self, item, key_values): # fixed
		key_indexes = sorted(list(map(lambda key: self.fields.index(key) + 1, key_values.keys())))
		groups = self.divide_list(key_indexes)
		for group in groups:
			row1 = group[0]
			row2 = group[-1]
			sheet_range = f'{self.sheet_page}!{item["_column"]}{row1}:{item["_column"]}{row2}'
			values = list(map(lambda index: key_values[self.fields[index - 1]], group))
			vertical_values = [[value] for value in values]
			body = {
				'range': sheet_range,
				'values': vertical_values,
				'majorDimension': 'ROWS'
			}
			self.perform_update_sheet_action(sheet_range, body)
		for key in key_values.keys():
			item[key] = key_values[key]

	def set_straight_items_values(self, item_value_tuples): # fixed
		key_values = item_value_tuples[0][1]
		key_indexes = sorted(list(map(lambda key: self.fields.index(key) + 1, key_values.keys())))
		groups = self.divide_list(key_indexes)
		for group in groups:
			row1 = group[0]
			row2 = group[-1]
			sheet_range = f'{self.sheet_page}!{item_value_tuples[0][0]["_column"]}{row1}:{item_value_tuples[-1][0]["_column"]}{row2}'
			values = []
			for index in group:
				sub_values = []
				for item_value_tuple in item_value_tuples:
					sub_values.append(item_value_tuple[1][self.fields[index - 1]])
				values.append(sub_values)
			body = {
				'range': sheet_range,
				'values': values,
				'majorDimension': 'ROWS'
			}
			self.perform_update_sheet_action(sheet_range, body)
		for item_value_tuple in item_value_tuples:
			for key in item_value_tuple[1].keys():
				item_value_tuple[0][key] = item_value_tuple[1][key]

	def set_items_values(self, item_value_tuples): # fixed
		groups = self.divide_list_verticaly(item_value_tuples)
		for group in groups:
			self.set_straight_items_values(group)

	def set_item_value(self, item, value, key=None): # fixed
		item[key] = value
		row = self.fields.index(key) + 1
		sheet_range = f'{self.sheet_page}!{item["_column"]}{row}'
		body = {
			'range': sheet_range,
			'values': [[value]],
			'majorDimension': 'ROWS'
		}
		self.perform_update_sheet_action(sheet_range, body)

	def refresh(self): # fixed
		self.items, self.fields = self.get_items()

	def url(self): # fixed
		return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"

	def duplicate_sheet(new_sheet_name, template_sheet_id="", folder_id="", users=[]): # fixed
		credentials_file = keychain.keys()["google_credentials_path"]
		credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=['https://www.googleapis.com/auth/drive'])

		drive_service = build('drive', 'v3', credentials=credentials)

		# Make a copy of the original spreadsheet
		copied_file = {'name': new_sheet_name}
		request = drive_service.files().copy(fileId=template_sheet_id, body=copied_file, fields='id, parents')
		file = request.execute()
		# Move the copied spreadsheet to the desired folder
		file_id = file['id']
		request = drive_service.files().update(
			fileId=file_id,
			addParents=folder_id,
			removeParents=file['parents'][0],
			fields='id, parents'
		)
		file = request.execute()

		# Share the copied spreadsheet with desired users
		batch = drive_service.new_batch_http_request()
		user_permission = {
			'type': 'user',
			'role': 'writer'
		}
		for email in users:
			user_permission['emailAddress'] = email
			batch.add(drive_service.permissions().create(
				fileId=file_id,
				body=user_permission,
				fields='id',
			))
		batch.execute()

		# Get the spreadsheet ID and URL
		spreadsheet_id = file['id']
		spreadsheet_url = 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id

		return spreadsheet_id, spreadsheet_url

	def create_sheet(sheet_name, folder_id="", users=[]): # fixed
		# Replace the placeholders with your values
		credentials_file = keychain.keys()["google_credentials_path"]

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

		return sheet_id, 'https://docs.google.com/spreadsheets/d/' + sheet_id

	def perform_get_sheet_action(self, range): # fixed
		try:
			return self.spreadsheets.values().get(spreadsheetId=self.sheet_id, range=range).execute()
		except HttpError as e:
			if e.resp.status == 429:
				# Quota exceeded, handle this error
				print("Spreadsheets quota exceeded. Waiting for 60 seconds before retrying...")
				time.sleep(60)
				# Retry the operation after waiting
				return self.perform_get_sheet_action(range)
			else:
				# Handle other HTTP errors here
				print(f"An HTTP error occurred: {e}")
				print("Sleeping for 10 seconds before retrying...")
				time.sleep(10)
				return self.perform_get_sheet_action(range)
		except Exception as e:
			# Handle other exceptions here
			print(f"An error occurred: {e}")
			return None

	def perform_update_sheet_action(self, range, body): # fixed
		try:
			result = self.spreadsheets.values().update(
				spreadsheetId=self.sheet_id, 
				range=range, 
				valueInputOption='USER_ENTERED', 
				body=body
			).execute()
		except HttpError as e:
			if e.resp.status == 429:
				# Quota exceeded, handle this error
				print("Spreadsheets quota exceeded. Waiting for 60 seconds before retrying...")
				time.sleep(60)
				# Retry the operation after waiting
				self.perform_update_sheet_action(range, body)
			else:
				# Handle other HTTP errors here
				print(f"An HTTP error occurred: {e}")
				print("Sleeping for 10 seconds before retrying...")
				time.sleep(10)
				self.perform_update_sheet_action(range, body)
		except Exception as e:
			# Handle other exceptions here
			print(f"An error occurred: {e}")
