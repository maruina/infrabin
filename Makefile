clean:
	./clean.sh

install-dev:
	pip install -e ".[dev]"

lint:
	flake8 src/ tests/

unittest: clean
	pytest tests -v

test: lint unittest


.PHONY: install-dev lint test
