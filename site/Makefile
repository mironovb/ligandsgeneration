# Makefile — one-command rebuild/serve for the Lanthanide Ligand Generation site.
# Run from the site/ directory:  make serve   (or: make build / figures / clean / install)
#
# The machine's system Ruby (2.6.10) is too old for this toolchain, so every recipe
# prepends Homebrew Ruby to PATH. This is Intel-Homebrew's path; on Apple Silicon run e.g.
#   make serve RUBY_BIN=/opt/homebrew/opt/ruby/bin
RUBY_BIN ?= /usr/local/opt/ruby/bin
EXPORT   := export PATH="$(RUBY_BIN):$$PATH";

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-10s %s\n", $$1, $$2}'

install: ## First-time setup: install gems locally into vendor/bundle
	$(EXPORT) bundle config set --local path 'vendor/bundle' && bundle install

serve: ## Build + serve with live reload at http://localhost:4000/
	$(EXPORT) bundle exec jekyll serve --livereload

build: ## Build the static site into _site/
	$(EXPORT) bundle exec jekyll build

figures: ## Regenerate the three SVG figures from verified numbers
	python3 assets/figures/make_figures.py

clean: ## Remove build output and caches
	rm -rf _site .jekyll-cache .jekyll-metadata

.PHONY: help install serve build figures clean
