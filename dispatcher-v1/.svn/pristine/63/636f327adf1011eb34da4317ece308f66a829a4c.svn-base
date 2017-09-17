# -*- coding: utf-8 -*-
"""
    管理应用的创建和配置流程
"""
import base64
import logging
import os
import time
import datetime
import hashlib

import httplib2
from flask import (current_app, Response, Blueprint, Flask, g, request)
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.auth.models import ComTempInfo
from app.configs.code import ResponseCode
from app.utils.client import MyOAuthCredentials, new_request, AccessTokenCredentialsError
from app.utils.helpers import json_dumps, json_loads
from app.utils.response import res
from flask_apscheduler import APScheduler
from app.configs.appwhitelist import app_white_list

# 引入扩展
from app.extensions import (db, login_manager, mail, redis_store, back_ground_scheduler,
                            migrate, csrf, celery, MySMTPHandler, NonASCIIJsonEncoder)  # 各种自定义帮助函数
from app.utils.tools import add_job_with_threads


def create_app(config=None):
    """创建应用"""

    # 初始化应用
    app = Flask("app")

    # 使用默认配置
    app.config.from_object('app.configs.default.DefaultConfig')
    # 更新配置
    app.config.from_object(config)
    # 尝试直接通过环境进行配置
    app.config.from_envvar("TOSC_SETTINGS", silent=True)

    # 配置celery初始化
    configure_celery_app(app, celery)
    # 配置蓝图
    configure_blueprints(app)
    # 配置扩展
    configure_extensions(app)

    # 配置应用程序上下文
    configure_context_processors(app)
    # 配置路由转发之前回调函数
    configure_before_handlers(app)
    # 配置路由转发之后回调函数
    configure_after_handlers(app)
    # 配置异常处理
    configure_errorhandlers(app)
    # 配置日志
    configure_logging(app)

    return app


def configure_celery_app(app, celery):
    """Configures the celery app."""
    app.config.update({'BROKER_URL': app.config["CELERY_BROKER_URL"]})
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask


def configure_blueprints(app):
    """
    上下文注册蓝图

    :param app: app
    """
    app_url_prefix = app.config['APP_URL_PREFIX']
    api_url_prefix = app.config['API_URL_PREFIX']

    def register_module_bp(model_obj, model_name, suffix_='app', url_prefix_=app_url_prefix):
        """
        sxw 2016 - 10 - 19

        注册蓝图

        :param model_obj: 模块对象
        :param model_name: 模块名
        :param suffix_: 前缀 app|api
        :param url_prefix_: url前缀，配置文件中配置
        """
        # 若包模块有标识符__load_app或_load_api且为True，则此模块注册，否则忽略
        load_flag_name = "__load_{}".format(suffix_)
        if not (hasattr(model_obj, load_flag_name) and getattr(model_obj, load_flag_name) is False):
            model_bp_name = "{}_{}_bp".format(model_name, suffix_)
            if hasattr(model_obj, model_bp_name):
                model_bp = getattr(model_obj, model_bp_name)
                if isinstance(model_bp, Blueprint) and model_bp not in app.blueprints:
                    app.register_blueprint(model_bp, url_prefix=url_prefix_)

    def register_module(model_obj, model_name):
        """
        sxw 2016-10-19

        分析模块，是否注册模块内应用

        :param model_obj:
        :param model_name:
        """
        if app.config['APP_ENABLE']:
            # 注册应用蓝图
            register_module_bp(model_obj, model_name, suffix_='app', url_prefix_=app_url_prefix)

        if app.config['API_ENABLE']:
            # 注册接口蓝图
            register_module_bp(model_obj, model_name, suffix_='api', url_prefix_=api_url_prefix)

    # 蓝图注册方式一，自动注册
    import pkgutil
    import importlib
    import app as app_
    package_path = app_.__path__
    package_name = app_.__name__
    import_error_bps = []
    for _, name, status in pkgutil.iter_modules(package_path):
        try:
            m = importlib.import_module('{0}.{1}'.format(package_name, name))
        except ImportError as e:
            import_error_bps.append((package_name, name))
            app.logger.error(
                "package_path:{}, package_name:{}, model_name:{}, except:{}\n{}, {}".format(package_path, package_name,
                                                                                            name,
                                                                                            e, _, status))
            continue
        else:
            register_module(m, name)
    for v in import_error_bps:
        package_name, name = v
        m = importlib.import_module('{0}.{1}'.format(package_name, name))
        register_module(m, name)


def load_app_request_token(request):
    """
    sxw 2016-10-19

    应用模块交互认证

    :param request: 请求句柄
    :return None: 为了兼容Flask-Login，返回空，Flask-Login认证失败
    """
    authorization = request.authorization

    # 从httplib2初始化一个http句柄
    h = httplib2.Http()

    if authorization:
        app_token = authorization.username
        key = hashlib.md5(app_token).hexdigest()
        # 初始化认证http，并将http和request附到g上
        http = current_app.oauth.authorize(h, app_token)
        g.http = http
        g.request = new_request
        temp = None
        client_name = current_app.config['CLIENT_NAME']
        # 先redis库中是否有相关用户缓存信息
        if current_app.config['REDIS_ENABLED']:
            temp = redis_store.hgetall(key)

        if not temp:
            from app.configs.api_uri import user as user_
            user_info_uri = user_.get_full_uri(user_.USER_MARKED_URI)

            body = {"sys_name": client_name}
            status, data, other = g.request(uri=user_info_uri, method='POST', body=body)

            # 请求用户信息成功，存库
            if status:
                g.user = data

                # 请求当前租户信息
                current_tenant_uri = user_.get_full_uri(user_.TENANT_CURRENT_URI)
                status, data, other = g.request(uri=current_tenant_uri, method='GET')
                if status:
                    g.tenant = data if data else {"tenant_id": 0, "name_en": "admin", "name_zh": "管理员",
                                                  "safety_flag": 1}

                    if current_app.config['REDIS_ENABLED']:
                        value = {
                            "app_token": app_token,
                            "user": json_dumps(g.user),
                            "tenant": json_dumps(g.tenant),
                        }
                        redis_store.hmset(key, value)
                        redis_store.expire(key, current_app.config['APP_TOKEN_EXPIRE'])
            # 打印错误日志
            if not status:
                current_app.logger.error("获取用户或租户信息失败，错误信息是:{}".format(data or other))
        else:
            g.user = json_loads(temp['user'])
            g.tenant = json_loads(temp['tenant'])

        # 标识当前操作是app模式且登录成功
        if g.user:
            g.app = True
            g.app_token = app_token

    # 暂时情况，针对开发过程中方便联调，实际生产过程删除此段代码
    elif current_app.config['DEBUG']:
        # 初始化认证http，并将http和request附到g上
        http = current_app.oauth.authorize(h)
        g.http = http
        g.request = new_request

    # finally, return None extend to flask-login
    return None


def load_api_request_token(request):
    """
    sxw 2016-10-19

    接口模块交互认证

    :param request:
    :return None: 为了兼容Flask-Login，返回空，Flask-Login认证失败
    """

    app_token = request.headers.get('app_token')
    pre_client_name = request.headers.get('client_name')
    pre_access_token = request.headers.get('access_token')

    # 从httplib2初始化一个http句柄
    h = httplib2.Http()

    if app_token and pre_client_name and pre_access_token:
        client_name = current_app.config['CLIENT_NAME']
        key = hashlib.md5(':'.join((app_token, pre_access_token))).hexdigest()
        # 初始化认证http，并将http和request附到g上
        http = current_app.oauth.authorize(h, app_token)
        g.http = http
        g.request = new_request
        temp = None
        # 先redis中是否有相关用户缓存信息
        if current_app.config['REDIS_ENABLED']:
            temp = redis_store.hgetall(key)

        # 未查询结果出来，先进行pre_access_token和pre_client_name的校验
        if not temp:
            from app.configs.api_uri import user as user_
            # 进行客户端校验
            status, data, other = g.request(uri=current_app.config['VERIFY3CLIENT_ACCESS_TOKEN_URI'], method='POST',
                                            body={"pre_access_token": pre_access_token,
                                                  "pre_client_name": pre_client_name})
            error_msg = u"app_token={},请求客户端client_name={},client_access_token={}，校验失败！".format(
                app_token, pre_client_name, pre_access_token)
            if status:
                # 校验客户端成功，进行用户相关信息校验
                user_info_uri = user_.get_full_uri(user_.USER_MARKED_URI)

                body = {"sys_name": client_name}
                status, data, other = g.request(uri=user_info_uri, method='POST', body=body)

                error_msg = u"app_token={},client_name={},client_access_token={},获取用户或租户信息失败！".format(
                    app_token, pre_client_name, pre_access_token)
                # 请求用户信息成功，存库
                if status:
                    user = data

                    # 请求当前租户信息
                    current_tenant_uri = user_.get_full_uri(user_.TENANT_CURRENT_URI)
                    status, data, other = g.request(uri=current_tenant_uri, method='GET')
                    if status:
                        error_msg = None
                        g.user = user
                        g.tenant = data if data else {"tenant_id": 0, "name_en": "admin", "name_zh": "管理员",
                                                      "safety_flag": 1}
                        g.api = True

                        if current_app.config['REDIS_ENABLED']:
                            value = {
                                "app_token": app_token,
                                "user": json_dumps(g.user),
                                "tenant": json_dumps(g.tenant),
                                "call_access_token": pre_access_token,
                            }
                            redis_store.hmset(key, value)
                            redis_store.expire(key, current_app.config['API_TOKEN_EXPIRE'] - 5)
            # 如果异常情况，记录日志信息
            if error_msg:
                current_app.logger.warning("{},{}".format(other, error_msg))

        else:
            g.user = json_loads(temp['user'])
            g.tenant = json_loads(temp['tenant'])
            g.api = True

        # 标识当前操作是api模式且登录成功
        if g.user:
            g.api = True
            g.app_token = app_token

    # 暂时情况，针对开发过程中方便联调，实际生产过程删除此段代码
    elif current_app.config['DEBUG']:
        # 初始化认证http，并将http和request附到g上
        http = current_app.oauth.authorize(h)
        g.http = http
        g.request = new_request

    # finally, return None extend to flask-login
    return None

def configure_extensions(app):
    """
    上下文插件扩展初始化配置

    :param app: app
    """
    # 设置flask-json支持中文
    app.json_encoder = NonASCIIJsonEncoder

    # Flask-WTF CSRF
    csrf.init_app(app)

    # Flask_apscheduler
    back_ground_scheduler.init_app(app)
    #
    #
    # add_job_with_threads()
    # back_ground_scheduler.add_listener(err_listener)
    # back_ground_scheduler.scheduler.add_listener(err_listener,EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_EXECUTED)
    # Flask-Plugins
    # plugin_manager.init_app(app)

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Migrate
    migrate.init_app(app, db)

    # Flask-Mail
    mail.init_app(app)

    # Flask-And-Redis
    redis_store.init_app(app)

    # Flask-Login
    login_manager.login_view = app.config["LOGIN_VIEW"]
    login_manager.refresh_view = app.config["REAUTH_VIEW"]
    login_manager.login_message_category = app.config["LOGIN_MESSAGE_CATEGORY"]
    login_manager.needs_refresh_message_category = \
        app.config["REFRESH_MESSAGE_CATEGORY"]

    @login_manager.user_loader
    def load_user(user_id):
        """
        user_id存储在flask的session环境中
        需要Flask-Login扩展，载入用户

        :param user_id:
        :return None:
        """
        return None

    @login_manager.token_loader
    def token_loader(token):
        """
        sxw 2016-6-24

        需要Flask-Login扩展，从cookie中获取令牌（token），进行解码分析，载入用户

        :param token:
        :return None:
        """
        return None

    @login_manager.request_loader
    def load_user_from_request(req):
        """
        sxw 2016-6-24

        需要Flask-Login扩展，可以从request-header中获取token，进行解码分析，载入用户

        :param req:
        :return None:
        """
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        """
        sxw 2016-6-24

        定制已经配置@login_required，但未登录的url请求错误

        :return json string:
        """
        return res(ResponseCode.NO_AUTHENTICATED)

    login_manager.init_app(app)

    # 开启支持OAuth2支持
    app.oauth = MyOAuthCredentials(None, app.config['CLIENT_NAME'], app.config['CLIENT_ID'],
                                   app.config['CLIENT_SECRET'], None, None,
                                   token_uri=app.config['GET_ACCESS_TOKEN_URI'])


def configure_context_processors(app):
    """
    配置应用上下文
    """
    pass

class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
            back_ground_scheduler.start()
        return cls._instance


def configure_before_handlers(app):
    """
    请求之前处理器

    :param app:
    """

    @app.before_first_request
    def initialize():
        # 第一次请求初始化
        # start_ = Singleton()
        back_ground_scheduler.start()

    @app.before_request
    def token_authentication():

        g.setdefault("user")
        g.setdefault("tenant")
        g.setdefault("token")

        if not g.user:
            if request.path.startswith(app.config['APP_URL_PREFIX']):
                load_app_request_token(request)

            if request.path.startswith(app.config['API_URL_PREFIX']):
                load_api_request_token(request)

        # 接口模式
        if request.path.startswith(app.config['API_URL_PREFIX']):
            access_token_url = app.config['API_URL_PREFIX'] + '/oauth/access_token'
            get_access_token_url = app.config['API_URL_PREFIX'] + '/access_token'
            if not (hasattr(g, 'api') and g.api or request.path in (access_token_url, get_access_token_url)):
                error_msg = u"禁止访问"
                return Response(error_msg, 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

        if request.path.startswith(app.config['APP_URL_PREFIX']):
            if not (hasattr(g, 'app')and g.app or request.path in app_white_list(app.config['APP_URL_PREFIX'])):
                return res(ResponseCode.ERROR, msg=u"禁止访问")

    @app.before_request
    def update_lastseen():
        """
        更新已认证用户的最后交互时间
        """
        pass
        # if current_user.is_authenticated:
        #     current_user.lastseen = datetime.datetime.now()
        #     db.session.add(current_user)
        #     db.session.commit()

    if app.config['REDIS_ENABLED']:
        @app.before_request
        def mark_current_user_online():
            pass


def configure_after_handlers(app):
    """
    sxw 2016-8-9

    请求之后处理器，非正常请求不处理

    :param app:
    """
    @app.teardown_request
    def teardown_request(exception):
        """
        sxw 2016-8-11
        针对模型query异常，回滚所有操作
        :param exception:
        :return:
        """
        if exception:
            db.session.rollback()
            db.session.remove()
        db.session.remove()


def configure_errorhandlers(app):
    """
    配置异常处理返回值

    :param app:
    """

    # @app.errorhandler(400)
    # def bad_request(error):
    #     error
    #     pass
    # if app.config['DEBUG'] is False:
    #     return res(400,)

    @app.errorhandler(404)
    def api_not_found(error):
        return res(ResponseCode.URL_NOT_FOUND)

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        sxw 2016-6-24

        定制405错误，若请求url路由存在但是未配置请求方式，则回复`请求方式错误，请重试`

        eg.
            @route('/api', method=['post'])
            get /api  则报这个错误
            post /api 则不报错

        :param error:
        :return:
        """
        return res(error.code, error.name)
        # return res(ResponseCode.METHOD_NOT_ALLOWED, u"请求方式错误，请重试!")

    @app.errorhandler(500)
    def server_error(error):
        return True

    from sqlalchemy.exc import SQLAlchemyError

    @app.errorhandler(SQLAlchemyError)
    def sql_alchemy_error(error):
        """
            sxw 2016-7-4

            处理sqlqlchemy异常错误
        """
        from _mysql_exceptions import OperationalError

        if not app.config['DEBUG'] and isinstance(error.orig, OperationalError):
            return res(ResponseCode.FLASK_SQLALCHEMY_EXCEPT, u"连接数据库操作异常，请联系管理员!")
        return res(ResponseCode.FLASK_SQLALCHEMY_EXCEPT, error.message)

    @app.errorhandler(AccessTokenCredentialsError)
    def access_token_error(error):
        """
            sxw 2017-3-9

            处理access token认证异常错误
        """
        return res(ResponseCode.TOKEN_CREDENTIALS_EXCEPT, error.message)


def configure_logging(app):
    """
    配置日志处理

    :param app:
    """
    # 根据时间分割日志文件
    logs_folder = os.path.join(app.root_path, os.pardir, "logs")
    logging.getLogger(app.config["LOGGER_NAME"])
    debug_formatter = logging.Formatter(app.config['DEBUG_FORMATTER'])
    info_formatter = logging.Formatter(app.config['INFO_FORMATTER'])
    error_formatter = logging.Formatter(app.config['ERROR_FORMATTER'])

    # 控制台文件中输出相应的日志信息
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(debug_formatter)
    app.logger.addHandler(stream_handler)

    import platform
    if "Linux" == platform.system():
        info_log = os.path.join(logs_folder, app.config['INFO_LOG'])

        info_file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=info_log,
            when=app.config['BACKUP_WHEN'],
            backupCount=app.config['BACKUP_COUNT']
        )

        info_file_handler.suffix = app.config['BACKUP_SUFFIX']
        info_file_handler.setLevel(logging.INFO)
        info_file_handler.setFormatter(info_formatter)
        app.logger.addHandler(info_file_handler)

        error_log = os.path.join(logs_folder, app.config['ERROR_LOG'])

        error_file_handler = logging.handlers.TimedRotatingFileHandler(
            error_log,
            when=app.config['BACKUP_WHEN'],
            backupCount=app.config['BACKUP_COUNT']
        )

        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.suffix = app.config['BACKUP_SUFFIX']
        error_file_handler.setFormatter(error_formatter)
        app.logger.addHandler(error_file_handler)

    if app.config["SEND_LOGS"]:
        mail_handler = MySMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['MAIL_DEFAULT_SENDER'][1],
            toaddrs=app.config['ADMINS'],
            subject='application error, no admins specified',
            credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
            ssl=True
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(error_formatter)
        app.logger.addHandler(mail_handler)

    # 设置系统默认日志记录等级
    app.logger.setLevel(logging.INFO)

    if app.config['SQLALCHEMY_ECHO']:
        # Ref: http://stackoverflow.com/a/842856
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement,
                                  parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement,
                                 parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            app.logger.debug('Total Time: %f', total)
