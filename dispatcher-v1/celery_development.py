#!/usr/bin/env python
"""
    app.celery_worker
    ~~~~~~~~~~~~~~~~~~~~~

    Prepares the celery app for the celery worker.
    To start celery, enter this in the console::

        celery -A celery_worker.celery --loglevel=info worker

    :copyright: (c) 2016 by the hddata Team.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from app.configs.development import DevelopmentConfig as Config
from app.application import create_app
from app.extensions import celery

app = create_app(Config)
