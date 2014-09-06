#!/usr/bin/python3

import sys
import os
import re
import json
import difflib

from hashlib import md5
from urllib.parse import urlsplit, quote, quote_plus, unquote
from urllib.request import urlopen, HTTPError

cache_dir = "cache"


def md5_url(url):
	return md5(url.encode("utf-8")).hexdigest()


def get_cache_filename(url):
	return os.path.join(cache_dir, md5_url(url))


def get_body(url):
	fname = get_cache_filename(url)
	if os.path.exists(fname):
		with open(fname, "rb") as f:
			return f.read()
	else:
		try:
			with urlopen(url) as o:
				body = o.read()
				with open(fname, "wb") as f:
					f.write(body)
				with open(fname + ".info.json", "w") as f:
					f.write(json.dumps({"url": url}))
				return body
		except HTTPError as e:
			body = e.fp.read()
			with open(fname, "wb") as f:
				f.write(body)
			with open(fname + ".info.json", "w") as f:
				f.write(json.dumps({"url": url}))
			return body


def lower_escapes(url):
	assert isinstance(url, bytes), type(url)
	if b'%' not in url:
		return url
	return re.sub(b'(%[a-fA-F0-9]{2})', lambda m: m.group(1).lower(), url)


def process_body(body, url):
	"""
	Return a post-processed page body that excludes irrelevant content
	that would prevent duplicate pages from being detected as duplicates.
	"""
	assert isinstance(body, bytes), type(body)
	u = urlsplit(url)
	if len(u.path) >= 5:
		path = u.path
		if path.startswith('/'):
			path = path[1:]
		body = body.replace(path.encode("utf-8"), b"")
		body = body.replace(path.encode("utf-8").replace(b"/", br"\/"), b"")
		body = body.replace(quote_plus(path).encode("utf-8"), b"")
		body = body.replace(lower_escapes(quote_plus(path).encode("utf-8")), b"")
		if '%' in path:
			unquoted_path = unquote(path)
			if len(unquoted_path) >= 4:
				body = body.replace(quote_plus(unquoted_path).encode("utf-8"), b"")
				body = body.replace(lower_escapes(quote_plus(unquoted_path).encode("utf-8")), b"")
	if len(u.query) >= 3:
		encoded_query = u.query.encode("utf-8")
		body = body.replace(('?' + u.query).encode("utf-8"), b"")
		body = body.replace(quote('?' + u.query).encode("utf-8"), b"")

	# Drupal generates a "theme_token":"..." inside a JSON blob
	body = re.sub(br'_token":"[-_A-Za-z0-9]+"', b"", body)

	if b"drupal" in body:
		# Drupal puts the current URL here, and the casing doesn't always match
		body = re.sub(br'<link rel="canonical" href="[^"]+" />', b"", body)

		# Drupal generates this form id
		body = re.sub(br'\bvalue="form-[-_A-Za-z0-9]+\b"', b"", body)

		# Drupal generates this class id
		body = re.sub(br"\bview-dom-id-[0-9a-f]+\b", b"", body)

		# Drupal generates <body class="..."> items based on the URL
		body = re.sub(br'<body class="[^"]+">', b"", body)

		# Drupal sites have randomized sidebar content with these IDs
		body = re.sub(br'<div class="views-field views-field-[-a-z]+">.*', b"", body)

	return body


def compare_bodies(body1, body2, url1, url2):
	# TODO: handle non-utf-8 bodies
	for line in difflib.unified_diff(
		body1.decode("utf-8").splitlines(keepends=True),
		body2.decode("utf-8").splitlines(keepends=True),
		fromfile=url1,
		tofile=url2):

		sys.stdout.write(line)


def compare_unprocessed_bodies(up_body1, up_body2, url1, url2):
	body1 = process_body(up_body1, url1)
	body2 = process_body(up_body2, url2)
	print("{} == md5({!r})".format(md5_url(url1), url1))
	print("{} == md5({!r})".format(md5_url(url2), url2))
	print("After processing,")
	print("len(body({!r})) == {}".format(url1, len(body1)))
	print("len(body({!r})) == {}".format(url2, len(body2)))
	compare_bodies(body1, body2, url1, url2)


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
		url1, url2 = sys.argv[1], sys.argv[2]
		compare_unprocessed_bodies(get_body(url1), get_body(url2), url1, url2)
	else:
		assert 0, sys.argv


if __name__ == '__main__':
	main()
