# -*- coding: utf-8 -*-

from app.cmdb import middleware
from app.cmdb import network
from app.cmdb import vm
from app.order.services import DisOrderService
from app.cmdb.constant import ResCMDBMapping
from app.cmdb.models import Dis_Alloc


class CMDBService(object):
    '''更新cmdb 删除记账表'''

    def __init__(self,order_id):
        self.order_id = order_id

    def get_service_type(self):
        order_info = DisOrderService.get_order_details(self.order_id)
        resource_type = order_info['resource_type']
        operation_type = order_info['operation_type']
        return resource_type,operation_type

    def update_cmdb(self):
        res_type, oper_type = self.get_service_type()
        resouce_operation = res_type + '_' + oper_type
        if ResCMDBMapping.mapping.has_key(resouce_operation):
            ResCMDBMapping.mapping[resouce_operation].update_cmdb(self.order_id)
        #销记账表
        Dis_Alloc.delete_alloc(self.order_id)



