export FLASK_APP=src/infrabin/app.py
export FLASK_DEBUG=1

clean:
	./clean.sh

install-dev:
	pipenv install -e .

lint:
	black src/ tests/
	flake8 src/ tests/

unittest: clean
	pytest -v tests

test: lint unittest

run:
	python3 src/infrabin/app.py
