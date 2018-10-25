from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), 'rb') as f:
    long_description = f.read().decode('utf-8')


setup(
    name='Flask-Babel',
    version='0.12.2',
    url='http://github.com/python-babel/flask-babel',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    description='Adds i18n/l10n support to Flask applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
