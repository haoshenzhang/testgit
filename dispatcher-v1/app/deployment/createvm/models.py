# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
预处理数据
daiguanlin
"""
from app.utils import format
from app.extensions import db
from sqlalchemy import text

from app.management.config_management.models import DisOffering,DisOpenstackFlavorRef

class Dis_Offering(object):
    """

    获取虚机配置id
    """
    @staticmethod
    def query_vm_config_by_id(offering_id):
        res = DisOffering.get_offering_by_id(offering_id=offering_id)
        res = format.format_result(res)[0]
        return res

class Dis_Openstack_Falor_Res(DisOpenstackFlavorRef):

    @staticmethod
    def get_falvor_id_by_offering(field, config_id):
        """
        获取虚机模板id
        :param field:
        :param config_id:
        :return:
        """
        sql = u"""
                    SELECT * FROM dis_openstack_flavor_ref WHERE offering_id = :offering_id
                """
        res = db.session.execute(text(sql), {'offering_id': config_id})
        res = format.FormatService.format_result(res)
        return res[0][field]

class Vm_fip():

    @staticmethod
    def update_fip_status(addr):
        """
        更新floating ip 的状态，改为使用中
        :param addr:
        :return:
        """
        sql = u"""
                UPDATE cmdb_ip SET status = :status WHERE addr = :addr
            """
        res = db.session.execute(text(sql), {'addr': addr,'status':u'使用中'})
