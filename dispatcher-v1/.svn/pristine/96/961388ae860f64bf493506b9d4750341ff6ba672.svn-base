# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
import requests
import json
from flask import g, current_app

from app.catalog.public_ip.models import DisResourceAllocate
from app.catalog.pyhsical_cluster.models import pm
from app.deployment.base.base import BaseAlloc,BaseBuildParm
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService
from app.utils import helpers

from app.configs.api_uri import network as net


class IPBuildParm(BaseBuildParm):
    def __init__(self, data, result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result


class GetIP(BaseAlloc):
    """
    分配ip/内网ip

    """
    def __init__(self, data, order_id):
        self.order_id = data['id']
        apply_info = helpers.json_loads(data['apply_info'])
        self.number = apply_info['number']
        self.subnet_id = helpers.json_loads(data['apply_info'])['private_net_name']
        self.formated_parm = helpers.json_dumps(self.format_para())

    def format_para(self):
        return dict(
            order_id=self.order_id,
            subnet_id=int(self.subnet_id),
            number=int(self.number)
        )

    def compute(self):
        ip_info_uri = net.get_full_uri(net.IP_MARKED_URI)
        current_app.logger.info(u"分配IP URL:{}".format(ip_info_uri))
        current_app.logger.info(u"分配IP POST DATA:{}".format(self.formated_parm))
        status, data, content = g.request(uri=ip_info_uri, body=self.formated_parm, method='post')
        if status:
            for i in content['data']['ip']:
                args = dict({"status": u"使用中", "id": i['id']})
                pm.update_ip_status(args)
                DisResourceAllocate.update_allocate_removed(self.order_id, 'VMWARE_IP')
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=i['addr'],
                    operation_name=u'alloc_ip',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                order_log_dict['execution_status'] = OrderStatus.succeed
                DisOrderLogService.created_order_log(order_log_dict)
            current_app.logger.info(u"调用network接口成功!")
            ip_alloc_data = dict(ip_alloc_info=content['data'])
            return ip_alloc_data
        else:
            order_log_dict = dict(
                order_id=self.order_id,
                operation_object='',
                operation_name='alloc_ip',
                execution_status=OrderStatus.doing
            )
            DisOrderLogService.created_order_log(order_log_dict)
            order_log_dict['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(order_log_dict)
            current_app.logger.info(u"调用network接口失败!")
            current_app.logger.error(u"失败原因:{}".format(content))
            return None



