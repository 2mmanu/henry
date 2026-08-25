.PHONY: install-dev run test lint format-check check

install-dev:
	python3 -m pip install -e '.[dev]'

run:
	python3 -m apps.control_plane

test:
	python3 -m unittest discover -s tests -v

lint:
	python3 -m ruff check .

format-check:
	python3 -m ruff format --check .

check: lint format-check test
