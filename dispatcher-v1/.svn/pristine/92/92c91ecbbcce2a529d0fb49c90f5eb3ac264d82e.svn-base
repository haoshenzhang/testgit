# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-14
    
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.recycle_net.views import RecycleNetList
from app.exceptions import errors

recycle_net = Api(catalog_app_bp, prefix="/catalog/recycle_net", errors=errors)

# 添加rest资源
recycle_net.add_resource(RecycleNetList, '/list')
