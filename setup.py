#!/usr/bin/env python3

import os, codecs
from os import path
from setuptools import setup

pwd = path.abspath(path.dirname(__file__))
with codecs.open(path.join(pwd, 'README.md'), 'r', encoding='utf8') as input:
	long_description = input.read()

name='STEP.py'
user='eddo888'
version='2.43'

setup(
	name=name,
	version=version,
	license='MIT',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/%s/%s'%(user,name),
	download_url='https://github.com/%s/%s/archive/%s.tar.gz'%(user, name, version),
	author='David Edson',
	author_email='eddo888@tpg.com.au',
	packages=[
		'STEP',
	],
	install_requires=[
		'argcomplete',
		'openpyxl',
		'xlrd',
		'xlwt',
		'dotmap',
		'pyxb',
		'suds-py3',
		'xmltodict',
		'Baubles',
		'Perdy',
		'Spanners',
		'Argumental',
		'GoldenChild',
		'Swapsies',
	],
	scripts=[
		'bin/step.soap.py',
		'bin/step.rest.py',
		'bin/excel2step.py',
		'bin/step2uml.py',
		'bin/uml2step.py',
		'bin/converter.py',
	],
)

