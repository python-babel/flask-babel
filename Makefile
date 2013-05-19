.PHONY: clean-pyc test upload-docs docs coverage

all: clean-pyc test

test:
	@nosetests -s

coverage:
	@rm -f .coverage
	@nosetests --with-coverage --cover-package=flask_babel --cover-html

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

docs:
	@$(MAKE) -C docs html

upload-docs: docs
	@python setup.py upload_sphinx
