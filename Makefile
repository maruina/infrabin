clean:
	./clean.sh

init:
	pip install pip==18.0
	pip install pipenv --upgrade

install:
	pipenv install --deploy --system --skip-lock

install-dev:
	pipenv install --dev --skip-lock

shell:
	pipenv shell

lint:
	black src/infrabin/ tests/
	flake8 --max-line-length=88 src/infrabin/ tests/

unittest: clean
	py.test -v tests

ci:
	pipenv run py.test -sv tests --cov=infrabin

run:
	./run.sh prod

run-dev:
	./run.sh dev