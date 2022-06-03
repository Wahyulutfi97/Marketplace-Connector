from setuptools import setup, find_packages

with open('requirements.txt') as f:
        install_requires = f.read().strip().split('\n')

# get version from __version__ variable in firebase/__init__.py
from firebase import __version__ as version
setup(
	name='marketplace_connector',
	version=version,
	description='App for managing marketplace',
	author='PT DAS',
	author_email='digitalasiasolusindo@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
