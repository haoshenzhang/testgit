#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-09-22

    记录用户操作日志模块
"""
from flask import Blueprint
from flask_restful import Api

from app.exceptions import errors
from app.log_.views import TenantLogs, UserLogs, TenantExportLogs, UserExportLogs, AdminLogs, AdminExportLogs

log__app_bp = Blueprint("log", __name__)

log_rest = Api(log__app_bp, prefix="/log", errors=errors)
log_rest.add_resource(AdminLogs, "/admin/logs")
log_rest.add_resource(AdminExportLogs, "/admin/export/logs")
log_rest.add_resource(TenantLogs, "/tenant/logs")
log_rest.add_resource(TenantExportLogs, "/tenant/export/logs")
log_rest.add_resource(UserLogs, "/user/logs")
log_rest.add_resource(UserExportLogs, "/user/export/logs")
