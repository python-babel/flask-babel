"""
Flask-BabelEx
-------------

Adds i18n/l10n support to Flask applications with the help of the
`Babel`_ library.

This is fork of official Flask-Babel extension with following features:

1. It is possible to use multiple language catalogs in one Flask application;
2. Localization domains: your extension can package localization file(s) and use them
   if necessary;
3. Does not reload localizations for each request.

Links
`````

* `documentation <http://packages.python.org/Flask-BabelEx>`_
* `development version
  <http://github.com/mrjoes/flask-babelex/zipball/master#egg=Flask-BabelEx-dev>`_
* `original Flask-Babel extension <https://pypi.python.org/pypi/Flask-Babel>`_.

.. _Babel: http://babel.edgewall.org/

"""
from setuptools import setup


setup(
    name='Flask-BabelEx',
    version='0.8.1',
    url='http://github.com/mrjoes/flask-babelex',
    license='BSD',
    author='Serge S. Koval',
    author_email='serge.koval+github@gmail.com',
    description='Adds i18n/l10n support to Flask applications',
    long_description=__doc__,
    packages=['flask_babelex'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Babel',
        'pytz',
        'speaklater>=1.2',
        'Jinja2>=2.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
