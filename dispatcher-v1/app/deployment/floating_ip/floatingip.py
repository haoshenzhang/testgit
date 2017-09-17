# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests

from app.order.constant import OrderStatus
from app.order.models import DisOrderLog
from app.order.services import DisOrderLogService
from app.utils import helpers
from app.management.logicpool.models import InfLogicPool
from app.deployment.base.base import BaseAlloc,BaseBuildParm
from app.configs.api_uri import network
from flask import g,current_app

class FIPBuildParm(BaseBuildParm):
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result


class GetFIP(BaseAlloc):
    def __init__(self, data,order_id):
        self.order_id = order_id
        self.apply_info = helpers.json_loads(data['apply_info'])
        self.number = self.apply_info['number']
        self.pool_id = self.apply_info['pool_id']
        self.virtual_type = InfLogicPool.query_user_virtualtype(self.pool_id)['virtualtype']
        if self.virtual_type == 'VMware':
            pass
        if self.virtual_type == 'Openstack':
            self.formated_parm = helpers.json_dumps(self.format_para())
            self.g_dict = self.format_para()

    def format_para(self):
        return dict(
            order_id = self.order_id,
            number = self.number,
            logic_pool_id = self.pool_id
        )

    def compute(self):
        fip_info_uri = network.get_full_uri(network.FLOATING_IP_MARKED_URI)
        if self.virtual_type == 'VMware':
            return {'VMware':'VMware_type'}
        if self.virtual_type == 'Openstack':
            if not hasattr(g, "request"):
                response = g.request(uri=fip_info_uri, body=self.formated_parm, method='post')
            else:
                current_app.logger.info(u"开始分配openstack floating ip ")
                current_app.logger.info(u"分配floating URL:" + fip_info_uri)
                status, data, content = g.request(uri=fip_info_uri, body=self.formated_parm, method='post')
                if status:
                    current_app.logger.info(u"分配成功 ")
                    ip_alloc_data = dict(fip_alloc_info=content['data'])
                    log = dict(
                        operation_name=u'alloc_floating_ip',
                        operation_object=u'floating_ip',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.succeed
                    DisOrderLogService.created_order_log(log)
                    return ip_alloc_data
                if content['status'] == '10001':
                    current_app.logger.info(u"调用network分配floating_ip接口失败!")
                    current_app.logger.error(u"失败原因:" + content['message'])
                    log = dict(
                        operation_name=u'alloc_floating_ip',
                        operation_object=u'floating_ip',
                        execution_status=u'doing',
                        order_id=self.order_id
                    )
                    DisOrderLog.created_order_log(log)
                    log['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(log)
                    return None


