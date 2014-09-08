#!/usr/bin/python3

import sys
import os
import json
import time

from dupespotter import process_body, compare_unprocessed_bodies

def main():
	start = time.time()
	for test_name in os.listdir("tests"):
		body_fnames = list(os.path.join("tests", test_name, f) for f in os.listdir(os.path.join("tests", test_name)) if not f.endswith(".info.json"))
		assert len(body_fnames) == 2, body_fnames
		body1 = open(body_fnames[0], "rb").read()
		body2 = open(body_fnames[1], "rb").read()
		url1 = json.loads(open(body_fnames[0] + ".info.json", "r").read())["url"]
		url2 = json.loads(open(body_fnames[1] + ".info.json", "r").read())["url"]
		print(test_name)
		compare_unprocessed_bodies(body1, body2, url1, url2)
		print()
	print("Done in %f seconds" % (time.time() - start,))


if __name__ == '__main__':
	main()
