HUGO ?= hugo
OINK_LOCAL ?= $(HOME)/pgsty/oink
PORT ?= 1313

# Keep local development independent of module workspaces and vendored pins.
export GOWORK := off
export HUGO_MODULE_WORKSPACE := off
PINNED_HUGO = env -u HUGO_MODULE_REPLACEMENTS $(HUGO)
LOCAL_HUGO = HUGO_MODULE_REPLACEMENTS="github.com/pgsty/oink -> $(abspath $(OINK_LOCAL))" $(HUGO) --ignoreVendorPaths=github.com/pgsty/oink

# 学习卡的构建产物（Hugo 会原样发布到 /cards/）
CARDS_OUT := static/cards/index.html

default: dev

# Development builds read the theme from the local OINK checkout at its
# current working state, not the version go.mod pins, so a theme change is
# visible here without a tag. Drafts, future and expired pages are all shown,
# and nothing is written to public/ -- the same shape as oink.pgsty.com's own
# `make dev`. Release targets keep the pinned module; check-local uses this checkout.
d:dev
dev: theme-local
	$(LOCAL_HUGO) server --renderToMemory -DFE --bind 127.0.0.1 --port "$(PORT)" --noBuildLock

serve:
	$(PINNED_HUGO) serve --environment production --minify --disableFastRender --disableLiveReload

b:build
build:
	$(PINNED_HUGO) build

cards:
	CARDS_OUT=$(CARDS_OUT) SITE_BASE= python3 cards/build.py

# 卡片是源（cards/src/*.md）渲染出的单文件产物；这里校验内容与产物都没有漂移。
cards-check:
	PYTHONDONTWRITEBYTECODE=1 python3 cards/check.py
	@tmp=$$(mktemp -d); \
	CARDS_OUT=$$tmp/index.html SITE_BASE= python3 cards/build.py >/dev/null; \
	if cmp -s $(CARDS_OUT) $$tmp/index.html; then \
		echo "✓ static/cards/index.html 与卡片源一致"; \
	else \
		echo "✗ static/cards/index.html 与卡片源不一致，请运行 make cards 重新生成"; \
		rm -rf $$tmp; exit 1; \
	fi; \
	rm -rf $$tmp

check: translation-check cards-check
	GOWORK=off go mod verify
	$(PINNED_HUGO) --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all

check-local: theme-local translation-check
	$(LOCAL_HUGO) --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all

.PHONY: default d dev serve b build check check-local cards cards-check

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
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all

epub:
	bin/epub

epub-check: epub
	bin/check-epub.py

.PHONY: translate translate-check figures figures-check translation-check translation-tests rendered-check epub epub-check

# Fail explicitly if a local theme was requested but is unavailable.
theme-local:
	@test -f "$(OINK_LOCAL)/hugo.yaml" || { echo "Set OINK_LOCAL to an OINK checkout (default: ~/pgsty/oink)." >&2; exit 1; }

.PHONY: theme-local
