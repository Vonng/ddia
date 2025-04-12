
default: doc

# serve document with docsify (or python)
doc:
	bin/doc

# generate zh-tw version
translate:
	bin/zh-tw.py

epub:
	bin/epub

.PHONY: default doc translate
