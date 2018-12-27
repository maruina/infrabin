export FLASK_APP=infrabin/app.py
export FLASK_DEBUG=1

clean:
	./clean.sh

init:
	pip install pipenv --upgrade

install-dev:
	pipenv install --dev --skip-lock

install:
	pipenv install --skip-lock

lint:
	black infrabin/ tests/
	flake8 --max-line-length=88 infrabin/ tests/

unittest: clean
	pytest -sv tests --cov=infrabin

test: lint unittest

run:
	PYTHONPATH="." python3 infrabin/app.py
