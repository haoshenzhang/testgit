# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    app.configs.production

    production configuration.
    :copyright: (c) 2016 by the HDDATA Team.
"""
import os

from datetime import timedelta

from celery.schedules import crontab

from app.configs.default import DefaultConfig
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class ProductionConfig(DefaultConfig):

    # 设置监听网段
    HOST = "0.0.0.0"

    # 设置运行端口号
    PORT = 5000

    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = 'mysql://developer:123456@10.237.43.27/travelclouddev?charset=utf8'

    # 不输出SQL语句
    SQLALCHEMY_ECHO = False

    # 系统密钥
    # This is the secret key that is used for session signing.
    # You can generate a secure key with os.urandom(24)
    SECRET_KEY = "SecretKeyForSessionSigning"

    # You can generate the WTF_CSRF_SECRET_KEY the same way as you have
    # generated the SECRET_KEY. If no WTF_CSRF_SECRET_KEY is provided, it will
    # use the SECRET_KEY.
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = "reallyhardtoguess"

    # TravelSky mail 开启SSL保护，关闭TLS，使用465端口
    MAIL_SERVER = "10.6.168.229"
    MAIL_PORT = 25
    MAIL_USE_SSL = False
    MAIL_USE_TLS = False
    MAIL_USERNAME = "teamwork@travelsky.com"
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = ("Default Sender", "teamwork@travelsky.com")
    # 系统管理员，接收相关系统错误日志邮件
    ADMINS = ["teamwork@travelsky.com"]

    # Error/Info Logging
    # If SEND_LOGS is set to True, the admins (see the mail configuration) will
    # recieve the error logs per email.
    SEND_LOGS = False

    # The filename for the info and error logs. The logfiles are stored at
    # tosc/logs
    INFO_LOG = "info"
    ERROR_LOG = "error"

    # 按照文件大小分割参数配置
    MAX_BYTES = 100000
    BACKUP_COUNT = 10

    # 按照时间分割参数配置
    BACKUP_WHEN = "midnight"
    BACKUP_COUNT = 62
    # 备份配置文件后缀名
    BACKUP_SUFFIX = "%Y%m%d-%H%M.log"

    # 日志格式化参数配置
    DEBUG_FORMATTER = "%(asctime)s %(levelname)s %(message)s"
    INFO_FORMATTER = "%(asctime)s %(levelname)s %(message)s"
    ERROR_FORMATTER = "%(asctime)s %(levelname)s %(module)s 6%(process)d %(thread)d %(message)s"

    # REDIS 配置
    REDIS_ENABLED = True
    REDIS_URL = "redis://:travelskyopenstackcloud@10.237.43.12:6379/0"
    REDIS_DATABASE = 0

    # Celery
    CELERY_BROKER_URL = 'amqp://guest:guest@10.237.43.7//'
    CELERY_RESULT_BACKEND = 'db+{}'.format(SQLALCHEMY_DATABASE_URI.split("?")[0])
    # CELERY_TASK_SERIALIZER = 'json'
    # CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    CELERY_IMPORTS = ("app.tasks",)

    # APP接口前缀
    APP_URL_PREFIX = "/app"

    # 设置用户操作日志开关
    SERVICE_LOG_ENABLED = True

    # 各个项目uri前缀地址，配置相应的ip，端口号，版本号
    INF_URI_PREFIX = 'http://10.237.43.8:5000'
    NET_URI_PREFIX = 'http://10.237.43.9:5000'
    OPR_URI_PREFIX = 'http://10.237.43.10:5000/api'
    DIS_URI_PREFIX = 'http://10.237.43.13:5000/api'
    BIZ_URI_PREFIX = 'http://10.237.43.15:5000/api'
    USER_URI_PREFIX = 'http://10.237.43.14:5000/api'

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
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time':3600*12
    }

    SCHEDULER_API_ENABLED = True