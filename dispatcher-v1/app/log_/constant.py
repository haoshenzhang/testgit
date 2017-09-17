# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-11-08

    日志模块常量定义
"""
import datetime
import random
import string

from flask.ext.restful import Resource

from app.utils.helpers import DBEnum


class LogLevel(DBEnum):
    """
    sxw 2016-9-22
    操作日志等级
    """
    error = u'ERROR'        # 错误
    warning = u'WARNING'    # 警告
    info = u'INFO'          # 通知


class RequestMethod(DBEnum):
    """
    sxw 2016-9-22
    请求方法方式
    """
    post = u'POST'
    delete = u'DELETE'
    put = u'PUT'
    get = u'GET'


class LogName(Resource):
    """
    whfang 2017-04-17
    日志名称
    """
    @staticmethod
    def log_name():
        log_time = datetime.datetime.now().strftime('%Y%m%d')
        random_number = string.join(
            random.sample(
                ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
                5)).replace(" ", "")
        return u'{}_{}_{}.pdf'.format(u'航信云日志', log_time, random_number)