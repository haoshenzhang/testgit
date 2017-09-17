# !/usr/bin/python
# -*- coding: utf-8 -*-

from flask_restful import Api

from app.exceptions import errors
from app.management import management_app_bp
from app.management.config_management.views import ConfigManagementApi, PmConfigApi, EnvironmentApi, \
    FlavorApi, EnableVmConfigApi, EnablePmConfigApi,FlavorByOfferingApi

config = Api(management_app_bp, prefix="/management/config", errors=errors)

# 添加rest资源
# 1.查询虚机配置 2.关联flavor 3.发布取消发布
config.add_resource(ConfigManagementApi, '/vmconfig')
# 查询未关联的env
config.add_resource(EnvironmentApi, '/env')
# 查询flavor 根据env_id
config.add_resource(FlavorApi, '/flavor')
# 查询可用虚机配置
config.add_resource(EnableVmConfigApi, '/enablevm')
# 查询可用物理机配置
config.add_resource(EnablePmConfigApi, '/enablepm')
# 查询所有物理机配置
config.add_resource(PmConfigApi, '/pmconfig')
# 1.查询关联的flavor通过offeringID 2. 取消关联根据offeringID和flavorid
config.add_resource(FlavorByOfferingApi, '/flavor_offering')
