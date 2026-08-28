OINK_MODULE := github.com/pgsty/oink
OINK_LOCAL := $(HOME)/pgsty/oink

default: dev

# Development builds read the theme from the local OINK checkout at its
# current working state, not the version go.mod pins, so a theme change is
# visible here without a tag. Drafts, future and expired pages are all shown,
# and nothing is written to public/ -- the same shape as oink.pgsty.com's own
# `make dev`. Every other target keeps the pinned module.
d:dev
dev:
	HUGO_MODULE_REPLACEMENTS="$(OINK_MODULE) -> $(OINK_LOCAL)" \
		hugo server --renderToMemory -DFE

serve:
	hugo serve --environment production --minify --disableFastRender --disableLiveReload

b:build
build:
	hugo build

check:
	GOWORK=off go mod verify
	GOWORK=off hugo --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings --panicOnWarning

check-local:
	HUGO_MODULE_REPLACEMENTS="$(OINK_MODULE) -> $(OINK_LOCAL)" \
		hugo --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings --panicOnWarning

.PHONY: default d dev serve b build check check-local

# generate zh-tw version
translate:
	uv run --with opencc-python-reimplemented==0.1.7 -- python bin/zh-tw.py

figures:
	bin/figure-layout.py --write

figures-check:
	bin/figure-layout.py --check

epub:
	bin/epub

epub-check: epub
	bin/check-epub.py

.PHONY: translate figures figures-check epub epub-check
