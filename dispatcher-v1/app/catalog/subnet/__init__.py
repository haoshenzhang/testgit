# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-01-09

    子网和vlan模块
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.subnet.views import (TenantCreateSubnet, TenantSubnet, UserSubnet, CheckSubnetName, TenantSubnetList,
                                      TenantVpcSubnetSelect, TenantVpcSubnetList, ChoseIpSegment, TenantSubnets,
                                      CheckName, CheckSegment, RecycleSubnets)
from app.catalog.subnet.views import TenantVmwareSubnet
from app.exceptions import errors

subnet_rest = Api(catalog_app_bp, prefix="/catalog/subnet", errors=errors)

subnet_rest.add_resource(TenantCreateSubnet, '/tenant/subnet')
subnet_rest.add_resource(TenantSubnet, '/tenant/subnet/<int:subnet_id>')
subnet_rest.add_resource(TenantSubnets, '/tenant/subnets')
subnet_rest.add_resource(TenantVmwareSubnet, '/tenant/vmware/subnet')
subnet_rest.add_resource(TenantSubnetList, '/tenant/subnet/list')

subnet_rest.add_resource(UserSubnet, '/user/subnet/<int:subnet_id>')
subnet_rest.add_resource(CheckSubnetName, '/check-name')
# add by zhouming 20170123 VPC下子网列表选择框
subnet_rest.add_resource(TenantVpcSubnetSelect, '/tenant/subnet/list/<int:vpc_id>')
# add by zhouming 20170206 VPC下子网列表
subnet_rest.add_resource(TenantVpcSubnetList, '/tenant/vpc/subnet/list/<int:vpc_id>')
subnet_rest.add_resource(ChoseIpSegment, '/vmware/chose-ip-segment')
# add by songxiaowei 2017-2-9 同一个vpc下校验子网名称是否重复
subnet_rest.add_resource(CheckName, '/vpc/<int:vpc_id>/check-name')
# add by songxiaowei 2017-2-9 同一个vpc下校验网段是否重复
subnet_rest.add_resource(CheckSegment, '/vpc/<int:vpc_id>/check-segment')
subnet_rest.add_resource(RecycleSubnets, '/tenant/recycle/subnets')

