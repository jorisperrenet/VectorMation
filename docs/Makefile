PYTHON ?= python
SPHINXBUILD ?= sphinx-build
SRCDIR = source
BUILDDIR = build

.PHONY: html assets clean serve live deploy help

help:  ## Show this help
	@grep -E '^[a-z][a-z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

html: assets  ## Build HTML docs (regenerates changed assets first)
	$(SPHINXBUILD) -b html $(SRCDIR) $(BUILDDIR)
	@echo "Build finished. Open $(BUILDDIR)/index.html"

assets:  ## Regenerate all assets (videos, SVGs, diagrams)
	$(PYTHON) build_assets.py

assets-force:  ## Rebuild all assets unconditionally
	$(PYTHON) build_assets.py --force

serve: html  ## Build and serve locally on port 8000
	$(PYTHON) -m http.server -d $(BUILDDIR) 8000

live:  ## Live-reload (requires sphinx-autobuild)
	sphinx-autobuild $(SRCDIR) $(BUILDDIR)

deploy: html  ## Deploy docs to GitHub Pages (gh-pages branch)
	@if [ ! -d $(BUILDDIR) ]; then echo "No build directory. Run 'make html' first."; exit 1; fi
	cd .. && ghp-import -n -p -f docs/build

clean:  ## Remove build directory
	rm -rf $(BUILDDIR)
