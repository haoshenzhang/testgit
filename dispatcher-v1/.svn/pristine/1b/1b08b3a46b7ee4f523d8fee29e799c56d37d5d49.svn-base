# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-29
    vpc创建rest资源注册
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.vpc.views import (Vpcs, CheckVpcName, CreateVpc, Vpc, TenantVpcSelect)
from app.exceptions import errors

vpc_rest = Api(catalog_app_bp, prefix="/catalog", errors=errors)
# 添加rest资源
vpc_rest.add_resource(Vpcs, '/vpcs')
vpc_rest.add_resource(CheckVpcName, '/vpc/check-name')
vpc_rest.add_resource(CreateVpc, '/vpc')
vpc_rest.add_resource(Vpc, '/vpc/<int:vpc_id>')
# add by zhouming 20170123 租户资源池下VPC选择框列表
vpc_rest.add_resource(TenantVpcSelect, '/vpc/tenant/select')

