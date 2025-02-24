#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, json

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.insert(0, '..')

from STEP.SOAP import *
from STEP.Cleaner import suds2dict

#_________________________________________________________________
def main():
	result = args.execute()
	if result:
		_colour = colour()
		if output():
			_colour = False
			_output = codecs.open(output(),'w',encoding='utf8')
		else:
			_output = sys.stdout
			
		prettyPrint(render(result),output=_output,colour=_colour)
		if output():
			print(output())
			_output.close()
		sys.exit(0)
	else:
		sys.exit(1)
		
#_________________________________________________________________
if __name__ == '__main__': main()
