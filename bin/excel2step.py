#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

# remove before flight
#sys.path.insert(0,'..')

from STEP.XML import Converter, args

print(args.execute())
