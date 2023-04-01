setup-dev-environment:
	pipenv install --dev

setup-container-environment:
	pipenv install --system --deploy

test:
	pytest . -vv

linting:
	black .

venv-shell:
	pipenv shell
