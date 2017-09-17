# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Author: jiagnxp
    createTime： 2016/8/1
    email:xpjiang@travesky.com
    Description;
"""
import sys
import threading

from flask import Flask, g, current_app, render_template, session

# 测试 和 生产 某些地址不一样 现在都是测试的
from app.extensions import back_ground_scheduler

config = {'CALLBACK_URL': 'http://10.6.144.228:8080', 'DOMAIN_URL': 'http://service.travelsky.net', 'DEPLOY': 'TEST',
          'JCF_TASK_URL': 'http://10.6.144.228:6260/jcf/', 'JCF_TASK_SWITCH': True}


class _MyLogger(object):
    def debug(self, msg):
        try:
            current_app.logger.debug(msg)
        except RuntimeError:
            file = sys.stderr
            print('DEBUG:%s' % msg, file)

    def info(self, msg):
        try:
            current_app.logger.info(msg)
        except RuntimeError:
            file = sys.stderr
            print('INFO:%s' % msg, file)

    def warning(self, msg):
        try:
            current_app.logger.warning(msg)
        except RuntimeError:
            file = sys.stderr
            print('WARNING:%s' % msg, file)

    def error(self, msg):
        try:
            current_app.logger.error(msg)
        except RuntimeError:
            file = sys.stderr
            print('ERROR:%s' % msg, file)

    def exception(self, msg):
        try:
            current_app.logger.exception(msg)
        except RuntimeError:
            file = sys.stderr
            print('EXCEPTION:%s' % msg, file)


logger = _MyLogger()


# 全局的日志对象，对于flask app是写入app.logger日志文件，对于celery app则直接打印到console
# 对于中文需要用unicode编码： logger.debug(u'你好')


def sub_string(str_):
    # 用逗号分隔字符串jiangxp 2016.8.1
    str2 = str_.split(',')
    return str2


# def read_list(list_):


def sub_string_url(str_):
    str2 = str_.split('/')
    ss = str2[1]
    l = len(ss)
    str2 = str_[l + 1:]
    return str2


def format_list2string(list_):
    str_ = ','
    return str_.join(list_)


def string2list2(str_):
    list_ = str_.split('.')
    return list_[-1]


def string2list3(str_):
    list_ = str_.split('.')
    del list_[-1]
    return list_


def my2list(str_, s_type):
    list_22 = str_.split(s_type)
    return list_22


def addr2list(str_):
    re_list = []
    list_ = str_.split('-')
    begin = string2list2(list_[0])
    end = string2list2(list_[1])
    li = string2list3(list_[0])
    for i in range(int(begin), int(end) + 1):
        li.append(str(i))
        ac = '.'.join(li)
        del li[-1]
        re_list.append(ac)
    return re_list


def json_dumps(obj):
    '''将对象转换成json字符串。默认json.dumps无法序列化Datetime对象，这里进行了特殊处理。
    @param obj: obj,待处理的对象
    @return: json string

    '''
    import json
    import datetime

    class MyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return str(obj)

            return json.JSONEncoder.default(self, obj)

    return json.dumps(obj, cls=MyEncoder, ensure_ascii=False)


def json_loads(obj):
    '''将json字符串转换成对象。
    @param obj: str,待处理的字符串
    @return: json object

    '''
    import json
    return json.loads(obj, cls=json.JSONDecoder, encoding="utf-8", strict=False)  # 设置encoding以支持中文，strict以支持控制字符


def now(valuet_='%Y-%m-%d %H:%M:%S'):
    '''返回当前时间字符串
    @param valuet: str, 时间格式定义字符串，默认值为'%Y-%m-%d %H:%M:%S'
    @return: str, 格式化的当前时间值，如2014-05-05 22:22:22

    '''
    return time.strftime(valuet_)


def error_page(e):
    '''错误响应页面。如果是调试模式则会直接抛出异常，否则拦截异常并显示页面
    @param e: exception object,异常对象
    @return: html

    '''
    pass


def simple_func():
    return None


def add_simple_job():
    back_ground_scheduler.add_job(id=u'simple_job', func=simple_func, trigger='interval', seconds=3600)


def add_job_with_threads():
    thread_ = threading.Thread(target=add_simple_job)
    thread_.start()

