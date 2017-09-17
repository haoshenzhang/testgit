# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -12-12
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.vpn.views import VpnList, VpnApp
from app.exceptions import errors

vpn = Api(catalog_app_bp, prefix='/catalog/vpn', errors=errors)
# 添加rest资源
vpn.add_resource(VpnApp, '/testyg/index')
vpn.add_resource(VpnList, '/list')
