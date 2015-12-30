"""
Flask-ICU
-----------

Adds i18n/l10n support to Flask applications with the help of the
`PyICU`_ library.

Links
`````

* `documentation <http://packages.python.org/Flask-ICU>`_
* `development version [Add later]`_ # TODO: Provide link to dev repo

.. _PyICU: https://pypi.python.org/pypi/PyICU/

"""
from setuptools import setup


setup(
    name='Flask-ICU',
    version='0.9',
    url='https://github.com/beavyHQ/flask-icu',
    license='BSD',
    author='Ethan Miller',
    author_email='ethan@code-cuts.com',
    description='Adds i18n/l10n support to Flask applications',
    long_description=__doc__,
    packages=['flask_icu'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'pyicu',
        'speaklater>=1.2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',  # TODO: update dev status
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
