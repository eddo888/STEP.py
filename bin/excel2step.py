#!/usr/bin/env python3

import sys, os, re

from STEP.XML import Converter

converter = Converter()
converter.process(sys.argv[1])
converter.close() # force close and save of id cache


