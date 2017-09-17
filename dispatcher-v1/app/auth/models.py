# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-11-06

    认证相关模型类
"""
from app.extensions import db
from app.utils.database import CRUDMixin


class ComTempInfo(db.Model, CRUDMixin):
    """
        sxw 2016-11-16

        各大系统缓存用户信息模型
    """
    __tablename__ = 'com_temp_info'

    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 针对一个库情下，区分不同的应用
    client_name = db.Column(db.String(255), nullable=False, index=True)
    # app_token，标识标识当前操作用户身份缓存，类似于openid
    app_token = db.Column(db.String(255), nullable=False, index=True)
    # 针对第三方平台调用传递的access_token
    call_access_token = db.Column(db.String(255))
    # 远程调用第三方平台对于的应用名
    call_client_name = db.Column(db.String(255))
    # 缓存的当前用户信息，json格式存储
    user = db.Column(db.JSON())     # 缓存用户数据
    # 缓存的分组信息，json格式存储
    group = db.Column(db.JSON())
    # 缓存的租户信息，json格式存储
    tenant = db.Column(db.JSON())
    # 缓存的其它信息，json格式存储
    other = db.Column(db.JSON())
    # 缓存创建时间
    created = db.Column(db.DateTime)
