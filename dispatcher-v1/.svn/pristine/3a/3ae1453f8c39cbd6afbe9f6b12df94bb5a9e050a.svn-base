# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.restful import Api

from app.catalog import catalog_app_bp
from app.catalog.bigeye_policy.views import BigeyePolicyApi
from app.exceptions import errors

bigeye = Api(catalog_app_bp, prefix="/catalog/bigeye_policy", errors=errors)
# 1.获取监控参数get 2.修改监控参数 put
bigeye.add_resource(BigeyePolicyApi, '/bigeye_policy')