# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-12-16
    
"""
from flask_restful import Api

from app.exceptions import errors
from app.security import security_app_bp
from app.security.member.views import SecurityListApi, SecurityApi

security = Api(security_app_bp, prefix="/security/member", errors=errors)

# 添加rest资源
security.add_resource(SecurityListApi, '/index')
security.add_resource(SecurityApi, '/list')
