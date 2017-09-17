# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Api

from app.exceptions import errors
from app.management import management_app_bp
from app.management.tenant_resource.views import TenantResourceApi, TenantListApi, PoolZoneApi, SecurityListApi, \
    SecurityTenantApi

tenant = Api(management_app_bp, prefix="/management/tenant", errors=errors)

# 租户资源操作
tenant.add_resource(TenantResourceApi, '/tenant_resource')
# 租户列表
tenant.add_resource(TenantListApi, '/tenant_list')
# zone和资源的树状结构
tenant.add_resource(PoolZoneApi, '/zone_pool')
# 安全服务列表
tenant.add_resource(SecurityListApi, '/security_list')
tenant.add_resource(SecurityTenantApi, '/tenant_security')

