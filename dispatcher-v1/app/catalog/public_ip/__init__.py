# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.restful import Api

from app.catalog import catalog_app_bp
from app.catalog.public_ip.views import PublicIpApi, RemovePublicIpApi, GetPublicIp, GetObject, BoundIp, UnBoundIp

from app.exceptions import errors

public_ip = Api(catalog_app_bp, prefix="/catalog/public_ip", errors=errors)

# 公网ip 1.列表get 2.回收站 delete 3.还原 put
public_ip.add_resource(PublicIpApi, '/index')
# 彻底删除delete
public_ip.add_resource(RemovePublicIpApi, '/remove')
# 查询租户下的公网ip地址（去除已绑定和正在绑定中的）
public_ip.add_resource(GetPublicIp, '/public_ip')
# 查询对象名称
public_ip.add_resource(GetObject, '/object')
# 绑定，修改名称及描述
public_ip.add_resource(BoundIp, '/bound')
# 解绑
public_ip.add_resource(UnBoundIp, '/unbound')



