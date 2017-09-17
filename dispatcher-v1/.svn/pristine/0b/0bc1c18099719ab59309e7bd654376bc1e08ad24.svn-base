# !/usr/bin/python
# -*- coding: utf-8 -*-

from flask_restful import Api

from app.exceptions import errors
from app.management import management_app_bp
from app.management.zone.views import ZoneApi, UpdateZoneApi, EnableZoneApi

zone = Api(management_app_bp, prefix="/management/zone", errors=errors)

# 添加rest资源
# zone 增删改查
zone.add_resource(ZoneApi, '/zone')
# 修改状态
zone.add_resource(UpdateZoneApi, '/updatezone')
# 查询可用zone接口
zone.add_resource(EnableZoneApi, '/enable_zone')
