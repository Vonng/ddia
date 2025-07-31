default: dev

d:dev
dev:
	hugo serve

b:build
build:
	hugo build

.PHONY: default d dev b build

# generate zh-tw version
translate:
	bin/zh-tw.py

epub:
	bin/epub

.PHONY: default doc translate
