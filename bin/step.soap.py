#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, json

from STEP.SOAP import *
from STEP.Cleaner import suds2dict

print(suds2dict(args.execute()))

