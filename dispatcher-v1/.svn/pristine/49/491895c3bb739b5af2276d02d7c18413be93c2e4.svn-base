#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-09-22

    日志模型文件
"""
import datetime
import re

from flask import current_app, g, request

from app.configs.default import DefaultConfig
from app.extensions import db
from app.log_.constant import RequestMethod, LogLevel
from app.log_.url_operation import url_method_operation_mapping
from app.utils.database import CRUDMixin
from app.utils.parser import parser_by_name


# 需要忽略的参数名词
IGNORE_ARGS_NAME = ["password", "passwd", "pwd"]


class ComUserLog(db.Model, CRUDMixin):
    """
    sxw 2016-9-22

    用户操作日志模型
    """
    __tablename__ = 'com_user_log'

    id = db.Column(db.Integer, primary_key=True)  # 日志编号
    # 操作用户id，注意，-1代表此用户未认证成功
    user_id = db.Column(db.Integer, nullable=False, server_default=db.text("'-1'"))
    user_name = db.Column(db.String(50, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False,
                          server_default=db.text("'匿名用户'"))  # 操作用户名
    # 操作用户所属租户id，注意，-1代表此用户未认证成功
    tenant_id = db.Column(db.Integer, nullable=False, server_default=db.text("'-1'"))
    login_ip = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)  # 操作用户ip
    port = db.Column(db.Integer, server_default=db.text("5000"))  # 端口号
    url = db.Column(db.String(255, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)  # 访问url
    # 访问前端url，用于后期添加链接快速跳转功能
    front_url = db.Column(db.String(255, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    method = db.Column(db.Enum(*RequestMethod.enums), nullable=False,
                       server_default=db.text(RequestMethod.post.value))  # 访问url
    level = db.Column(db.Enum(*LogLevel.enums), nullable=False,
                      server_default=db.text(LogLevel.info.value))  # 访问等级
    model = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))  # 模块名
    place = db.Column(db.String(255, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)  # 对应界面上操作
    operation = db.Column(db.JSON())  # 访问操作内容
    create_date = db.Column(db.DateTime, nullable=False)  # 访问时间
    update_date = db.Column(db.DateTime)  # 结束访问时间
    result_code = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))  # 返回结果状态编码
    result_msg = db.Column(db.String(255, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))  # 放回结果信息
    remark = db.Column(db.String(500, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))  # 备注信息

    def __init__(self, action, resource, id_name=None):
        if g.user:
            self.user_id = g.user.get("current_user_id")
            self.user_name = g.user.get("user_real_name")
        if g.tenant:
            self.tenant_id = g.tenant.get("tenant_id")
        if request.args.get("place"):
            self.place = request.args.get("place")
        if request.args.get("front_url"):
            self.front_url = request.args.get("front_url")
        self.login_ip = request.remote_addr
        self.port = current_app.config["PORT"]
        self.url = request.path
        self.method = request.method
        self.level = LogLevel.info.value
        if self.method.upper() in [RequestMethod.post.value, RequestMethod.put.value]:
            self.level = LogLevel.warning.value
        # 迭代url_operation列表
        # songxiaowei 2017-03-24，装饰器方法实现操作记录，不需要进行简单的转换
        # for url in url_method_operation_mapping:
        #     url_re = r"^{}{}$".format(current_app.config["APP_URL_PREFIX"], url[0])
        #     if re.match(url_re, self.url):
        #         self.operation = url[1].get(self.method.upper(), u"此操作未入库，请联系相关人员入库")
        #         break
        # else:
        #     self.operation = u"此操作未入库，请联系相关人员入库"
        self.operation = {"action": action, "resource_type": resource}
        # 提取id值
        # 根据id值的变量名提取id值，参数分为2类，
        # 1为字符串类型
        # 2为list或tuple
        if id_name:
            if isinstance(id_name, basestring):
                id_ = parser_by_name(id_name)
                id_ = {"id": id_}
            elif isinstance(id_name, (list, tuple)):
                id_ = {"id": {id_name: parser_by_name(id_name) for id_name in id_name}}
            else:
                raise TypeError("id_name参数类型错误!")
            self.operation.update(id_)

        # 将参数值压入操作对象中
        kwargs = dict(request.args) if hasattr(request, "args") and request.args else {}
        kwargs.update(dict(request.form) if hasattr(request, "form") and request.form else {})
        if hasattr(request, "json") and request.json:
            if isinstance(request.json, dict):
                kwargs.update(dict(request.json))
            elif isinstance(request.json, list):
                kwargs.update({"request-json": request.json})
        kwargs = {k_.lower(): v for k_, v in kwargs.items()}
        for k in IGNORE_ARGS_NAME:
            # 将敏感词置不可读
            if k in kwargs:
                kwargs[k] = "******"
        self.operation.update({"args": kwargs})

        self.model = current_app.config['CLIENT_NAME']
        self.create_date = datetime.datetime.now()

