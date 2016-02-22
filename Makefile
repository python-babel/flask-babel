.PHONY: clean-pyc test upload-docs

all: clean-pyc test

test:
	@cd tests; py.test tests.py

tox-test:
	@tox

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean: clean-pyc

upload-docs:
	$(MAKE) -C docs html
	python setup.py upload_docs

.PHONY: upload-docs clean-pyc clean tox-test test all
