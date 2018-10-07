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

lint:
	black infrabin/ tests/
	flake8 --max-line-length=88 infrabin/ tests/

unittest: clean
	pipenv run py.test -v tests

ci: lint
	pipenv run py.test -sv tests --cov=infrabin

run:
	python3 infrabin/app.py
