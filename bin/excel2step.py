#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

if sys.argv[0].startswith('.'):
	sys.path.insert(0,'..')

from STEP.XML import Converter, args

print(args.execute())
