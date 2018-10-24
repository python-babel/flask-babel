"""
Flask-Babel
-----------

Adds i18n/l10n support to Flask applications with the help of the
`Babel`_ library.

Links
`````

* `documentation <http://packages.python.org/Flask-Babel>`_
* `development version
  <http://github.com/mitsuhiko/flask-babel/zipball/master#egg=Flask-Babel-dev>`_

.. _Babel: http://babel.edgewall.org/

"""
from setuptools import setup


setup(
    name='Flask-Babel',
    version='0.12.0',
    url='http://github.com/python-babel/flask-babel',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    description='Adds i18n/l10n support to Flask applications',
    long_description=__doc__,
    packages=['flask_babel'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'Babel>=2.3',
        'Jinja2>=2.5'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
