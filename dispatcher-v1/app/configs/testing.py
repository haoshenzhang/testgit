# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    app.configs.testing
    ~~~~~~~~~~~~~~~~~~~
    This is the app's testing config.
    :copyright: (c) 2016 by the HDDATA Team.
"""
from datetime import timedelta

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from celery.schedules import crontab

from app.configs.default import DefaultConfig


class TestingConfig(DefaultConfig):

    # 设置监听网段
    HOST = "0.0.0.0"

    # 设置运行端口号
    PORT = 5000

    # Indicates that it is a testing environment
    DEBUG = False
    TESTING = False

    # 测试环境数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://developer:123456@10.237.43.127/travelclouddev?charset=utf8'

    # This will print all SQL statements
    SQLALCHEMY_ECHO = False

    # Security
    SECRET_KEY = "SecretKeyForSessionSigning"
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = "reallyhardtoguess"

    # Error/Info Logging
    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    SEND_LOGS = False
    # 设置日志执行级别，应用中配置了相应的日志记录，禁用默认的
    LOGGER_HANDLER_POLICY = "never"

    # Flask-Redis
    REDIS_ENABLED = True
    REDIS_URL = "redis://:travelskyopenstackcloud@10.237.43.105:6379/0"
    REDIS_DATABASE = 0

    # Celery
    CELERY_BROKER_URL = 'amqp://test:test123456@10.237.43.118/user'
    CELERY_RESULT_BACKEND = 'db+{}'.format(SQLALCHEMY_DATABASE_URI.split("?")[0])

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    # CELERY_IMPORTS = ("tasks",)

    # APP接口前缀
    APP_URL_PREFIX = "/app"

    # 设置用户操作日志开关
    SERVICE_LOG_ENABLED = True

    # 各个项目uri前缀地址，配置相应的ip，端口号，版本号
    INF_URI_PREFIX = 'http://10.237.43.119:5000'
    NET_URI_PREFIX = 'http://10.237.43.120:5000'
    OPR_URI_PREFIX = 'http://10.237.43.121:5000'
    DIS_URI_PREFIX = 'http://10.237.43.122:5000/api'
    BIZ_URI_PREFIX = 'http://10.237.43.123:5000/api'
    USER_URI_PREFIX = 'http://10.237.43.126:5000/api'

    # 认证相关接口配置
    GET_ACCESS_TOKEN_URI = '{}/oauth/access_token'.format(USER_URI_PREFIX)
    VERIFY3CLIENT_ACCESS_TOKEN_URI = '{}/oauth/auth3client'.format(USER_URI_PREFIX)

    # 配置Celery定时任务
    CELERYBEAT_SCHEDULE = {
        'add-every-10-seconds': {
            'task': 'app.tasks.add',
            'schedule': timedelta(seconds=10),
            'args': (16, 16)
        },
        'add-every-monday-morning': {
            'task': 'app.tasks.add',
            'schedule': crontab(hour=9, minute=0, day_of_week=[1, 2, 3, 4, 5]),
            'args': (23, 23),
        },
    }

    # Apscheduler
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 100
    }

    SCHEDULER_API_ENABLED = True


