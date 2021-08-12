
default: serve

# serve document with docsify (or python)
serve:
	bin/serve

# generate zh-tw version
translate:
	bin/zh-tw.py

.PHONY: default serve translate
