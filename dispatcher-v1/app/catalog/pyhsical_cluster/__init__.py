# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -12-05
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.pyhsical_cluster.views import PhysicalClusterDiskApp, PhysicalClusterApp, PmApp, PmClusterCreateApp, \
    PmCreateApp
from app.exceptions import errors


pyhsical_cluster = Api(catalog_app_bp, prefix='/catalog/pyhsical_cluster', errors=errors)
# 添加rest资源
pyhsical_cluster.add_resource(PhysicalClusterDiskApp, '/disk/add')

pyhsical_cluster.add_resource(PhysicalClusterApp, '/cluster/list')

pyhsical_cluster.add_resource(PmApp, '/pm/list')

pyhsical_cluster.add_resource(PmClusterCreateApp, '/cluster/create')

pyhsical_cluster.add_resource(PmCreateApp, '/pm/create')