# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
from flask_restful import (Api)

from app.exceptions import errors
from app.catalog import catalog_app_bp
from app.catalog.fw.views import fworderApi, AppGetResource, Getlist, Recycleinfo, Deletefw,FwListSearch,FwRecover


fw = Api(catalog_app_bp, prefix='/catalog/fw', errors=errors)

fw.add_resource(fworderApi, '/test')
fw.add_resource(AppGetResource, '/get_resource')
fw.add_resource(Getlist, '/getresourcelist')
fw.add_resource(Recycleinfo, '/recycleinfo')
fw.add_resource(FwRecover, '/recoverinfo')
fw.add_resource(Deletefw, '/deletefw')
fw.add_resource(FwListSearch,'/list')


