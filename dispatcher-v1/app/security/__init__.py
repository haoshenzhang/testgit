# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-25
    
"""
from flask import Blueprint

security_app_bp = Blueprint("security", __name__)
# 引用注册的rest路由规则
from app.security import member
