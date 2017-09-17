#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.auth

    sxw 2016-8-12

    注册蓝图
"""
from flask import Blueprint

auth_app_bp = Blueprint("auth", __name__)

# 引入模块，执行注册的路由，若放到开头，则造成循环引入问题
from app.auth import views

auth_api_bp = Blueprint("auth_api", __name__)

# 引入模块，执行注册的路由，若放到开头，则造成循环引入问题
from app.auth import api
