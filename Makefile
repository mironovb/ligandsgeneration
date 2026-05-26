# Root convenience Makefile — proxies to site/Makefile so you can build and serve the
# documentation site from the repo root. The real recipes (and the Homebrew-Ruby PATH
# handling the toolchain needs) live in site/Makefile.
.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-10s %s\n", $$1, $$2}'

install: ## First-time setup: install the site's gems into site/vendor/bundle
	$(MAKE) -C site install

serve: ## Build + serve the site with live reload at http://localhost:4000/
	$(MAKE) -C site serve

build: ## Build the static site into site/_site/
	$(MAKE) -C site build

figures: ## Regenerate the site's SVG figures from verified numbers
	$(MAKE) -C site figures

clean: ## Remove the site's build output and caches
	$(MAKE) -C site clean

.PHONY: help install serve build figures clean
