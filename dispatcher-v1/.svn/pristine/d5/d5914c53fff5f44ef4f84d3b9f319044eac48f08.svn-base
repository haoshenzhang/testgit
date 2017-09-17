# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-06
    
"""
from flask_restful import Api

from app.catalog import catalog_app_bp
from app.catalog.backup_policy.views import BackupPolicyApi, BackupPolicyList, BackupPolicyListByCondition
from app.exceptions import errors

backup = Api(catalog_app_bp, prefix="/catalog/backup_policy", errors=errors)

# 添加rest资源
backup.add_resource(BackupPolicyApi, '/index')
backup.add_resource(BackupPolicyList, '/restore')
backup.add_resource(BackupPolicyListByCondition, '/list')
