# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: CC0-1.0

# `make install` copies the built theme into the system paths, as a package
# does; `make install-defaults` adds the optional defaults. Neither changes
# any setting. PREFIX, LIBDIR and SYSCONFDIR follow the usual conventions.
DESTDIR ?=
PREFIX ?= /usr
LIBDIR ?= $(PREFIX)/lib64
SYSCONFDIR ?= /etc
INSTALL := python3 tools/install.py --destdir "$(DESTDIR)" --prefix "$(PREFIX)" --libdir "$(LIBDIR)" --sysconfdir "$(SYSCONFDIR)"

# The remote targets (deploy, install-user, install-root, plymouth, verify,
# screens, fetch-screenshots) are only a development helper: build on this
# machine, then apply the theme on a test machine over SSH with the scripts in
# tools/dev/, which change its settings. Name it with TARGET=user@host.
TARGET ?=
REMOTE := .cache/halloween-openSUSE
VENV := tools/.venv
PY := $(VENV)/bin/python

.PHONY: all need-target build check lint dist release-check install install-defaults uninstall deploy install-user install-root plymouth verify screens fetch-screenshots previews icon-preview clean

all: check

$(VENV)/.ok: tools/requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r tools/requirements.txt
	touch $@

$(VENV)/.dev: tools/requirements-dev.txt $(VENV)/.ok
	$(VENV)/bin/pip install -q -r tools/requirements-dev.txt
	touch $@

# zizmor's online audits (known-vulnerable actions, impostor commits) need a
# GitHub token; CI runs them with ZIZMOR_FLAGS=--format=github.
ZIZMOR_FLAGS ?= --offline

lint: $(VENV)/.dev
	$(VENV)/bin/ruff check tools
	$(VENV)/bin/shellcheck -x -P tools/dev tools/*.sh tools/dev/*.sh tools/dev/vm/*.sh
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" $(VENV)/bin/actionlint
	$(VENV)/bin/zizmor $(ZIZMOR_FLAGS) .github
	$(VENV)/bin/typos
	$(VENV)/bin/ec
	$(VENV)/bin/reuse lint

build: $(VENV)/.ok
	$(PY) tools/build.py

check: build
	$(PY) tools/check.py

release-check: build
	$(PY) tools/check.py --release

dist:
	tools/dist.sh

# These use only the files in build/: run `make check` first, as yourself.
install:
	$(INSTALL)

install-defaults:
	$(INSTALL) --defaults

uninstall:
	$(INSTALL) --uninstall
	$(INSTALL) --uninstall --defaults

need-target:
	@test -n "$(TARGET)" || { echo "name the test machine: make $(MAKECMDGOALS) TARGET=user@host" >&2; exit 1; }

deploy: need-target check
	tools/deploy.sh $(TARGET)

install-user: deploy
	ssh $(TARGET) $(REMOTE)/install/install-user.sh

install-root: deploy
	ssh -t $(TARGET) sudo $(REMOTE)/install/install-root.sh

plymouth: need-target
	ssh -t $(TARGET) sudo $(REMOTE)/install/install-root.sh --plymouth

verify: need-target
	ssh $(TARGET) $(REMOTE)/install/verify.sh

screens: need-target
	ssh $(TARGET) $(REMOTE)/install/test-screens.sh all

fetch-screenshots: need-target
	rsync -a $(TARGET):$(REMOTE)/screenshots/ art/screenshots/

previews: $(VENV)/.ok
	$(PY) tools/previews.py

icon-preview: build
	$(PY) tools/icon_preview.py

clean:
	rm -rf dist build/user build/root build/firefox build/defaults build/install build/*.txt build/*.json build/MANIFEST.sha256
