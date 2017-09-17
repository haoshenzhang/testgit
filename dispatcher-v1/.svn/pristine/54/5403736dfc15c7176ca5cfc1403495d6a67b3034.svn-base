# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -12-16
"""
from flask_restful import Api

from app.catalog.volume import VolumeListApi
from app.exceptions import errors
from app.overview import overview_app_bp
from app.overview.resource_overview.views import PmVmApi, InternetIPApi, VolumeApi

overview = Api(overview_app_bp, prefix="/overview/resource", errors=errors)
overview.add_resource(PmVmApi, '/pmvm/index')
overview.add_resource(InternetIPApi, '/internetip/index')
overview.add_resource(VolumeApi, '/volume/index')