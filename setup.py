from setuptools import setup, find_packages

setup(
    name='carlo',
    version='0.1.64',
    description='Description of your package',
    packages=find_packages(),
    install_requires=[
        'google-auth',
        'google-api-python-client',
        'openai',
        'google-cloud-storage',
        'python-wordpress-xmlrpc'
    ],
)