# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-09-13

    定时任务模块
"""
from app.extensions import celery
from app.log_.models import ComUserLog
from flask import current_app


@celery.task
def add(x, y):
    return x + y


@celery.task
def select_async_temp():
    result = ComUserLog.query.all()
    current_app.logger.error(result)


def select_temp():
    select_async_temp.delay()

