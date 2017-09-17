# -*- coding: utf-8 -*-
"""
    app.auth.views

    用户注册、认证视图层
"""
from flask import current_app

from app.auth import auth_api_bp
from app.utils.response import res


@auth_api_bp.route("/access_token")
def access_token():
    return res(data=current_app.config['access_token'])
