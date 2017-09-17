# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Api

from app.exceptions import errors
from app.management import management_app_bp
from app.management.logicpool.views import LogicPoolApi, ClusterApi, PoolTenantApi, PoolStatusApi

logicpool = Api(management_app_bp, prefix="/management/logicpool", errors=errors)

# 添加rest资源
# 客户资源池增删改查
logicpool.add_resource(LogicPoolApi, '/logicpool')
# 修改资源池状态
logicpool.add_resource(PoolStatusApi, '/pool_status')
# 底层资源树状结构
logicpool.add_resource(ClusterApi, '/cluster')
# 根据租户id查询客户资源池信息(get)
logicpool.add_resource(PoolTenantApi, '/pool_tenant')




