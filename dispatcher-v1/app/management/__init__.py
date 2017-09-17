# !/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint

management_app_bp = Blueprint("management", __name__)
# 引用注册的rest路由规则

from app.management.zone import zone
from app.management.logicpool import logicpool
from app.management.image import image
from app.management.config_management import config
from app.management.tenant_resource import tenant

