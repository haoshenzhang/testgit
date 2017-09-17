# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    wyj -12-28
"""
from flask_restful import Api
from app.catalog.f5.views import f5orderApi,AppGetF5Resource,GetF5list,F5Recycleinfo,Deletef5,F5ListSearch,F5Recover
from app.exceptions import errors
from app.catalog import catalog_app_bp

f5 = Api(catalog_app_bp, prefix='/catalog/f5', errors=errors)

f5.add_resource(f5orderApi, '/test')
f5.add_resource(AppGetF5Resource, '/get_resource')
f5.add_resource(GetF5list, '/getresourcelist')
f5.add_resource(F5Recycleinfo, '/recycleinfo')
f5.add_resource(F5Recover, '/recoverinfo')
f5.add_resource(Deletef5, '/deletef5')
f5.add_resource(F5ListSearch,'/list')
#测试URL
#http://127.0.0.1:5002/app/f5/getresource?app_id=1

