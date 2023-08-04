import requests, base64
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods.media import UploadFile

class WordPress:
	domain = ""
	user = ""
	app_password = ""

	def __init__(self, domain, user, app_password):
		self.domain = domain
		self.user = user
		self.app_password = app_password

	def auth_header(self):
		credentials = self.user + ":" + self.app_password
		token = base64.b64encode(credentials.encode())
		return {'Authorization': 'Basic ' + token.decode('utf-8')}

	def page_folder(self, slug):
		if "/" in slug:
			return "/".join(slug.split('/')[:-1])
		else:
			return ""
		
	def page_slug(self, slug):
		if "/" in slug:
			return slug.split('/')[-1]
		else:
			return slug

	def get_post(self, slug):
		folder = self.page_folder(slug)
		page_slug = self.page_slug(slug)
		api_url = f'https://{self.domain}/wp-json/wp/v2/{folder}?slug={page_slug}'
		response = requests.get(api_url)
		response_json = response.json()
		return response_json

	def publish_post(self, slug, data):
		folder = self.page_folder(slug)
		page_slug = self.page_slug(slug)
		response = self.get_post(slug)
		if len(response) == 1:
			api_url = f'https://{self.domain}/wp-json/wp/v2/{folder}/{response[0]["id"]}'
			print(f'Updating post https://{self.domain}/{folder}/{page_slug}')
			response = requests.post(api_url, headers=self.auth_header, json=data)        
			return response
		else:
			api_url = f'https://{self.domain}/wp-json/wp/v2/{folder}'
			print(f'Creating post https://{self.domain}/{folder}/{page_slug}')
			response = requests.post(api_url, headers=self.auth_header, json=data)
			return response
		
	def upload_image(self, local_file, file_type="image/jpeg"):
		wp_url = f'https://{self.domain}/xmlrpc.php'
		client = Client(wp_url, self.user, self.app_password)
		image_data = {
			'name': local_file.split("/")[-1],
			'type': file_type,
			'bits': xmlrpc_client.Binary(open(local_file, 'rb').read())
		}
		response = client.call(UploadFile(image_data))
		return WordPressImage(response["id"], response["url"])
	
class WordPressImage:
	id = ""
	url = ""

	def __init__(self, id, url):
		self.id = id
		self.url = url