
default: doc

# serve document with docsify (or python)
doc:
	bin/doc

# generate zh-tw version
translate:
	bin/zh-tw.py

.PHONY: default doc translate
