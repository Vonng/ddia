
default: serve

# serve document with docsify (or python)
s: serve
d: serve
serve:
	bin/serve

# generate zh-tw version
translate:
	bin/zh-tw.py

.PHONY: s d serve translate
