#!/usr/bin/env python

import sys
import pprint
import operator
from optparse import OptionParser

try:
	import yaml
except ImportError:
	print ("PyYAML library missing, try: yum install pyyaml")
	sys.exit(1)

# diff two list-of dicts for perf numbers
# this means just produce xfer_size, Gb/sec, usec/xfer
def _diff(a,b):
	r = []

	for v1, v2 in zip(a,b):
		d = {}
		for k in v2.keys():
			if k == 'xfer_size':
				d[k] = v2[k]
			elif k == 'Gb/sec' or k == 'usec/xfer':
				d[k] = v2[k] - v1[k]
			else:
				continue

		r.append(d.copy())

	return r

def difference(ystream):
	"""Subtract a from b and print the results"""

	# reverse stream and split based on key
	rev = reversed(list(ystream))
	a, b = {}, {}
	for i in rev:
		if not set(i).issubset(set(b)):
			b.update(i)
		else:
			a.update(i)

	result = {}
	for k in b.keys():
		result[k] = _diff(a[k], b[k])

	return result

def pretty(stream):
	"""Prety-print given yaml stream and exit"""
	for i in stream: pprint.pprint(i)
	return 0

def perfprint(d):
	for k,v in d.items():
		print k, ":"
		for i in v:
			print 'xfer_size: ', i['xfer_size'],
			print ', Gb/sec: %+f' % i['Gb/sec'],
			print ', usec/xfer: %+f' % i['usec/xfer']
	

def main(argv=None):

	parser = OptionParser(description='fabtests yaml parsing utility')
	parser.add_option('-d', action='store_true', default=False, help=difference.__doc__)
	parser.add_option('-v', action='store_true', default=False, help=pretty.__doc__)
	(options, args) = parser.parse_args()

	if len(args) == 0:
		fd = sys.stdin
	elif len(args) > 1:
		class fd:
			@staticmethod
			def read():
				r1 = map(open, args)
				r2 = map(lambda x: x.read(), r1) 
				return reduce(operator.add, r2)
	else:
		fd = open(args[0], 'r')

	yi = yaml.load_all(fd.read())

	if options.d:
		perfprint(difference(yi))

	if options.v:
		pretty(yi)

	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
