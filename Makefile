export FLASK_APP=src/infrabin/app.py
export FLASK_DEBUG=1

clean:
	./clean.sh

init:
	pip install pipenv --upgrade

install-dev:
	pipenv install --dev --skip-lock

shell:
	pipenv shell

lint: shell
	black infrabin/ tests/ setup.py
	flake8 infrabin/ tests/ setup.py

unittest: shell clean
	pipenv run py.test -v tests

ci: lint
	pipenv run py.test -sv tests --cov=infrabin

run: shell
	python3 infrabin/app.py
