HUGO ?= hugo
OINK_LOCAL ?= $(HOME)/pgsty/oink
PORT ?= 1313

# Keep local development independent of module workspaces and vendored pins.
export GOWORK := off
export HUGO_MODULE_WORKSPACE := off
PINNED_HUGO = env -u HUGO_MODULE_REPLACEMENTS $(HUGO)
LOCAL_HUGO = HUGO_MODULE_REPLACEMENTS="github.com/pgsty/oink -> $(abspath $(OINK_LOCAL))" $(HUGO) --ignoreVendorPaths=github.com/pgsty/oink

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

check: translation-check
	GOWORK=off go mod verify
	$(PINNED_HUGO) --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all

check-local: theme-local translation-check
	$(LOCAL_HUGO) --cleanDestinationDir \
		--printPathWarnings --printI18nWarnings
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all

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

# ---------------------------------------------------------------------------
# Vietnamese edition (fork nguyendan07/ddia). Appended block; upstream targets
# above are untouched. hugo.vi.yaml overlays hugo.yaml.
VI_HUGO = $(PINNED_HUGO) --config hugo.yaml,hugo.vi.yaml
# Must match baseURL in hugo.vi.yaml; CI passes the GitHub Pages URL.
BASE_URL ?= https://nguyendan07.github.io/ddia/
VI_ORIGIN = $(shell echo '$(BASE_URL)' | sed -E 's#^(https?://[^/]+).*#\1#')
VI_PATH = $(shell echo '$(BASE_URL)' | sed -E 's#^https?://[^/]+##')

# Copy every untranslated zh page to content/vi as a draft; never overwrite.
stubs:
	@mkdir -p content/vi
	@for f in content/zh/*.md; do \
		t=content/vi/$${f##*/}; \
		[ -e "$$t" ] && continue; \
		sed '1a draft: true\nbook_status: draft' "$$f" > "$$t" && echo "created $$t"; \
	done

vi-dev:
	$(VI_HUGO) server -D --baseURL / --renderToMemory --bind 127.0.0.1 --port "$(PORT)" --noBuildLock

vi-build:
	$(VI_HUGO) --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings --baseURL "$(BASE_URL)"

.PHONY: stubs vi-dev vi-build

# Drafts included so every link between pages resolves; the site is mounted at
# its real sub-path so links missing the base path fail. Deploys use vi-build.
vi-check:
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-vi.py
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bin/tests -p 'test_check_vi.py'
	PYTHONDONTWRITEBYTECODE=1 python3 bin/glossary-vi.py check
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s bin/tests -p 'test_glossary_vi.py'
	rm -rf tmp/site
	$(VI_HUGO) -D --printPathWarnings --printI18nWarnings --baseURL "$(BASE_URL)" -d "tmp/site$(VI_PATH)"
	PYTHONDONTWRITEBYTECODE=1 python3 bin/check-rendered-links.py --all --public tmp/site --origin "$(VI_ORIGIN)"

.PHONY: vi-check

# Cổng xuất bản: không còn thuật ngữ todo trong glossary sách và chương đã xuất bản.
vi-release-check:
	PYTHONDONTWRITEBYTECODE=1 python3 bin/glossary-vi.py check --release

.PHONY: vi-release-check
