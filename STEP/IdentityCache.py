#!/usr/bin/env python3

import os, re, sys, json, uuid, hashlib, arrow

class IdentityCache(object):

	filename = '.IdentityCache.json'

	#_____________________________________________
	def __init__(self):
		if os.path.isfile(self.filename):
			with open(self.filename) as input:
				self.cache = json.load(input)
		else:
			self.cache = dict()


	#_____________________________________________
	def save(self):
		with open(self.filename, 'w') as output:
			json.dump(self.cache, output, indent=4, sort_keys=True)


	#_____________________________________________
	def hasher(self, text):
		m = hashlib.md5()
		m.update(text.encode('utf8'))
		return m.hexdigest().upper()


	#_____________________________________________
	def has(self,key):
		return key in self.cache.keys()


	#_____________________________________________
	def get(self, key):
		if key not in self.cache.keys():
			id = '%s'%self.hasher(key)
			self.cache[key] = id
		return self.cache[key]


def main():
	cache = IdentityCache()
	now = arrow.now()
	url = 'https://docs.python.org/3/library/hashlib.html' #?_=%s'%now
	id = cache.get(url)

	print(id)


if __name__ == '__main__': main()
