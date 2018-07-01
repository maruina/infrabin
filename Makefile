export FLASK_APP=src/infrabin/app.py
export FLASK_DEBUG=1

clean:
	./clean.sh

install-dev:
	pipenv install -e .

lint:
	black src/ tests/ setup.py
	flake8 src/ tests/ setup.py

unittest: clean
	pytest -v tests

test: lint unittest

run:
	python3 src/infrabin/app.py
