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

check: translation-check
	GOWORK=off go mod verify
	GOWORK=off hugo --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings --panicOnWarning
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --second-edition

check-local: translation-check
	HUGO_MODULE_REPLACEMENTS="$(OINK_MODULE) -> $(OINK_LOCAL)" \
		hugo --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings --panicOnWarning
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --second-edition

.PHONY: default d dev serve b build check check-local

# Generate the second edition; preserve the first-edition manuscripts.
translate:
	uv run --with opencc-python-reimplemented==0.1.7 -- python bin/zh-tw.py --edition v2

translate-check:
	PYTHONDONTWRITEBYTECODE=1 uv run --with opencc-python-reimplemented==0.1.7 -- python bin/zh-tw.py --edition v2 --check

figures:
	bin/figure-layout.py --write

figures-check:
	bin/figure-layout.py --check

# Source checks are read-only; rendered checks require an existing Hugo build.
translation-check: translation-tests translate-check
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-translation.py
	PYTHONDONTWRITEBYTECODE=1 python3 bin/emphasis-style.py --check
	bin/figure-layout.py --check

translation-tests:
	PYTHONDONTWRITEBYTECODE=1 uv run --with opencc-python-reimplemented==0.1.7 -- python -m unittest discover -s bin/tests -p 'test_*.py' -v

rendered-check:
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --second-edition

epub:
	bin/epub

epub-check: epub
	bin/check-epub.py

.PHONY: translate translate-check figures figures-check translation-check translation-tests rendered-check epub epub-check
