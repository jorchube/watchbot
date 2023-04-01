setup-dev-environment:
	pipenv install --dev

setup-prod-environment:
	pipenv install

test:
	pytest . -vv

linting:
	black .

venv-shell:
	pipenv shell
