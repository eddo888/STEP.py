#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, json

from STEP.REST import *

result = args.execute()
if type(result) in [list, dict]:
	json.dump(result, sys.stdout, indent=4)
else:
	print(result)

