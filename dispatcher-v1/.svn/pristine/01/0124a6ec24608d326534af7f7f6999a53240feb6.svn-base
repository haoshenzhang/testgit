# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    dgl -12-05
"""
from flask_restful import Api

from app.catalog.vmhost.views import VMHostApi,VMActionAPI,VMOfferingApi,VMTemplateApi,VMUpdateInfo,\
    VMUpdateOffering,VMListApi,VMTestApi,VMDeleteApi,VMRecoverApi,VMRemoveApi,VMTakeOverApi
from app.exceptions import errors
from app.catalog import catalog_app_bp

vm = Api(catalog_app_bp, prefix="/catalog/vm", errors=errors)

# 添加rest资源
vm.add_resource(VMHostApi, '/create')
vm.add_resource(VMActionAPI,'/action')
vm.add_resource(VMDeleteApi,'/delete')
vm.add_resource(VMRecoverApi,'/recover')
vm.add_resource(VMRemoveApi,'/remove')

vm.add_resource(VMOfferingApi,'/offering')
vm.add_resource(VMTemplateApi,'/template')

vm.add_resource(VMUpdateInfo,'/update/info')
vm.add_resource(VMUpdateOffering,'/update/offering')
vm.add_resource(VMListApi,'/list')

# 虚机接管api
vm.add_resource(VMTakeOverApi, '/takeover')

# 测试用
vm.add_resource(VMTestApi,'/test')