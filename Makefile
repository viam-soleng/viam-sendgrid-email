.PHONY: build run install-test-deps test test-individual coverage

run:
	./run.sh

install-test-deps:
	pip install -r tests/requirements-test.txt

test: install-test-deps
	pytest -xvs tests/ --asyncio-mode=auto

test-individual: install-test-deps
	pytest -xvs tests/test_sendgrid_email.py --asyncio-mode=auto

coverage: install-test-deps
	python -m coverage run -m pytest tests/ --asyncio-mode=auto
	python -m coverage report
	python -m coverage html
