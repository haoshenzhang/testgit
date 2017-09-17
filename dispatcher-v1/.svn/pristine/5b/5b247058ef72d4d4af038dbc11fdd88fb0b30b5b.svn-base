# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
预处理数据
"""
from flask import current_app
from app.extensions import back_ground_scheduler
from app.utils import format
from app.extensions import db
from sqlalchemy import text

from app.management.config_management.models import DisOffering
from app.management.image.models import DisOsTemplate

class Dis_Offering(DisOffering):

    @staticmethod
    def query_vm_config():
        res = Dis_Offering.get_all_vm_config()
        res = format.format_result(res)
        return res

class Dis_Os_Template(DisOsTemplate):

    @staticmethod
    def query_vm_os_type():
        res = DisOsTemplate.get_os_list()
        res = format.format_result(res)
        return res

    @staticmethod
    def get_image_by_os(os_type):
        res = DisOsTemplate.get_image_by_os(os_type)
        res = format.format_result(res)
        return res

class Tenant_Openstack_Ref(object):

    @staticmethod
    def get_project_id_by_teannt(pool_id , tenant_id):
        sql_select = u"""
                    SELECT * FROM inf_pool_tenant_ref  WHERE tenant_id = :tenant_id AND pool_id = :pool_id
                    """
        template = db.session.execute(text(sql_select),{'tenant_id':tenant_id,'pool_id':pool_id})
        return template

def task_test():
    ctx = back_ground_scheduler.app.app_context()
    print ctx
    ctx.push()
    print '1024'
    current_app.logger.info(u"pooling 测试测试测试======================")
    res = DisOsTemplate.get_os_list()
    res = format.format_result(res)
    current_app.logger.info(res)
    ctx.pop()