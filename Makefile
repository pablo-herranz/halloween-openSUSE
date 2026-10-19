# SPDX-FileCopyrightText: 2026 Martin Pluskal <martin@pluskal.org>
# SPDX-License-Identifier: CC0-1.0

HOST ?=
TARGET ?=
REMOTE := .cache/halloween-openSUSE
VENV := tools/.venv
PY := $(VENV)/bin/python

.PHONY: all build check release-check deploy install-user install-root plymouth verify screens fetch-screenshots previews icon-preview clean

all: check

$(VENV)/.ok: tools/requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r tools/requirements.txt
	touch $@

build: $(VENV)/.ok
	$(PY) tools/build.py

check: build
	$(PY) tools/check.py

release-check: build
	$(PY) tools/check.py --release

deploy: check
	tools/deploy.sh $(TARGET)

install-user: deploy
	ssh $(TARGET) $(REMOTE)/install/install-user.sh

install-root: deploy
	ssh -t $(TARGET) sudo $(REMOTE)/install/install-root.sh

plymouth:
	ssh -t $(TARGET) sudo $(REMOTE)/install/install-root.sh --plymouth

verify:
	ssh $(TARGET) $(REMOTE)/install/verify.sh

screens:
	ssh $(TARGET) $(REMOTE)/install/test-screens.sh all

fetch-screenshots:
	rsync -a $(TARGET):$(REMOTE)/screenshots/ art/screenshots/

previews: $(VENV)/.ok
	$(PY) tools/previews.py

icon-preview: build
	$(PY) tools/icon_preview.py

clean:
	rm -rf build/user build/root build/firefox build/install build/*.txt build/*.json build/MANIFEST.sha256
