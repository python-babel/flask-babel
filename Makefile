.PHONY: clean-pyc test upload-docs

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

upload-docs:
	@$(MAKE) -C docs html
	@python setup.py upload_sphinx
