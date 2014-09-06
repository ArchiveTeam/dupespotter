#!/usr/bin/python3

import sys
import os

from hashlib import md5
from urllib.request import urlopen

cache_dir = "cache"


def get_cache_filename(url):
	return os.path.join(cache_dir, md5(url.encode("utf-8")).hexdigest())


def get_body(url):
	fname = get_cache_filename(url)
	if os.path.exists(fname):
		with open(fname, "rb") as f:
			return f.read()
	else:
		with urlopen(url) as o:
			body = o.read()
			with open(fname, "wb") as f:
				f.write(body)
			return body


def main():
	try:
		os.makedirs(cache_dir)
	except OSError:
		pass

	assert os.path.exists(cache_dir)

	if len(sys.argv) == 2:
		# Just save and print the body
		print(get_body(sys.argv[1]))
	elif len(sys.argv) == 3:
		first = get_body(sys.argv[1])
		second = get_body(sys.argv[2])
	else:
		assert 0, sys.argv


if __name__ == '__main__':
	main()
