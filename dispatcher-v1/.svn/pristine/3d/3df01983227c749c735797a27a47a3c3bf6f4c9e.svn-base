#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=======
TOSC是中航信分支机构云平台项目
其是一个基于微框架Flask的python编写的软件.
简单运行命令
-----------------
.. code:: bash
    $ python manage.py createall

    $ python manage.py runserver
     * Running on http://localhost:5000/
"""
from __future__ import print_function
from __future__ import absolute_import
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

VERSION = __import__('app').__version__


class PyTestCommand(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def __init__(self):
        self.pytest_args = None
        self.test_suite = False
        self.test_args = None

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        self.test_args = []

    def run_tests(self):
        import pytest
        err_no = pytest.main(self.pytest_args)
        sys.exit(err_no)


class WTForms(object):
    pass


setup(
    name='TOSC',
    version=VERSION,
    description=u'分支机构云平台',
    long_description=__doc__,
    author=u'HDData Team',
    author_email='hddata@travelsky.com',
    url='http://www.cloud-dc.cn/',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    py_modules=['wsgi', 'celery_worker'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'alembic',
        'aniso8601',
        'APScheduler',
        'Babel',
        'backports.shutil-get-terminal-size',
        'backports.ssl-match-hostname',
        'BareNecessities',
        'BeautifulSoup',
        'beautifulsoup4',
        'blinker',
        'certifi',
        'click',
        'colorama',
        'coverage',
        'decorator',
        'enum34',
        'Flask',
        'Flask-BabelPlus',
        'Flask-JSONRPC',
        'Flask-Login',
        'Flask-Mail',
        'Flask-Migrate',
        'Flask-MySQLdb',
        'Flask-Plugins',
        'Flask-Redis',
        'Flask-REST',
        'Flask-RESTful',
        'Flask-Restless',
        'Flask-Script',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'funcsigs',
        'itsdangerous',
        'Jinja2',
        'Mail',
        'Mako',
        'MarkupSafe',
        'mimerender',
        'mysqlclient',
        'passlib',
        'pathlib2',
        'pbr',
        'pickleshare',
        'prompt-toolkit',
        'Pygments',
        'pymongo-amplidata',
        'PyMySQL',
        'python-dateutil',
        'python-editor',
        'python-memcached',
        'python-mimeparse',
        'pytz',
        'redis',
        'requests',
        'selenium',
        'setuptools',
        'simplegeneric',
        'simplejson',
        'six',
        'speaklater',
        'sqlacodegen',
        'SQLAlchemy',
        'sqlalchemy-migrate',
        'SQLAlchemy-Utils',
        'sqlparse',
        'subprocess32',
        'Tempita',
        'traitlets',
        'tzlocal',
        'Unidecode',
        'urllib3',
        'wcwidth',
        'Werkzeug',
        'win-unicode-console',
        'WTForms',
        'celery'
    ],
    test_suite='tests',
    tests_require=[
        'py',
        'pytest',
        'pytest-cov',
        'pytest-random'
    ],
    dependency_links=[
        'https://github.com/jshipley/Flask-WhooshAlchemy/archive/master.zip#egg=Flask-WhooshAlchemy',
    ],
    classifiers=[
        'Development Status :: 1-Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers, Users',
        # 'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'test': PyTestCommand}
)
