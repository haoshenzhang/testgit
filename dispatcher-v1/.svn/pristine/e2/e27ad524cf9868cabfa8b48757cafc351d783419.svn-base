# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-07
    
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.recycle_policy.views import RecycleListApi, RecycleApi, RecycleUpdate
from app.exceptions import errors

recycle = Api(catalog_app_bp, prefix="/catalog/recycle_policy", errors=errors)

# 添加rest资源
recycle.add_resource(RecycleListApi, '/list')
recycle.add_resource(RecycleApi, '/index')
recycle.add_resource(RecycleUpdate, '/update')
