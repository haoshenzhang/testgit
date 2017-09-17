# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-28
    
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.volume.views import VolumeListApi
from app.exceptions import errors

volume = Api(catalog_app_bp, prefix="/catalog/volume", errors=errors)

# 添加rest资源
volume.add_resource(VolumeListApi, '/index')
