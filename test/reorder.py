#!/usr/bin/env python3

import os, re, sys

file=sys.argv[1]
lines = open(file).read().split('\n')

counter = 1
pattern = re.compile('^(\s+def\stest)_(\d\d)_(.*)')

with open(file,'w') as output:
	for line in lines:
		match = pattern.match(line)
		if match:
			lead, index, tail = tuple(match.groups())
			changed = f'{lead}_{counter:02d}_{tail}'
			print(changed)
			output.write(f'{changed}\n')
			counter += 1
		else:
			output.write(f'{line}\n')
			
