#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, json

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.insert(0, '..')

from STEP.REST import *

result = args.execute()
if type(result) in [list, dict]:
	json.dump(result, sys.stdout, indent=4)
else:
	print(result)

