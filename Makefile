setup-dev-environment:
	pipenv install --dev

test:
	pytest . -vv

linting:
	black .

venv-shell:
	pipenv shell
