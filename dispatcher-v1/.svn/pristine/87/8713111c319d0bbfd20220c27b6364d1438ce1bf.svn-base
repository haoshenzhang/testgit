# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
import json

from flask import current_app

from app.cmdb.vm.models import CmdbHostLogicserver
from app.configs.api_uri import network
from app.deployment.base.base import BaseWorker
from app.utils import client


class TakeOverVpnPolicy(BaseWorker):
    """
    数据接管调用VPN策略接口
    """

    def start_work(self):
        self.pre()
        self.target_address = self.vm_ip
        self.address_id = self.vm_ip_id
        self.g_dict = self.format_para()
        current_app.logger.info(u"开始接管虚机分配vpn策略")
        vpn_policy_uri = network.get_full_uri(network.CREATE_VPN)
        # full_url = 'http://10.237.43.103:5001/api/network/vpn/index'
        status, data, content = client.task_request(uri=vpn_policy_uri, body=self.g_dict, method='put',
                                                    app_token=self.app_token)
        current_app.logger.info(u"调用完成")
        if status:
            current_app.logger.info(u"调用接口成功")
            self.add_async_task(interval_time=20)
            return True, 'start work'
        else:
            current_app.logger.info(u"调用失败:{},{}".format(status, data))
            return None

    def pre(self):
        current_app.logger.info(u"当前编号为:{}".format(self.item_no))
        self.order_apply_info.replace('null', 'None')
        vm_list_info = eval(self.order_apply_info)
        vm_info = vm_list_info['vm_list']
        vm_info = vm_info[self.item_no]
        self.tenant_id = vm_list_info['tenant_id']
        self.vm_ip = vm_info['ip']
        ip_dict = dict(
            addr=self.vm_ip
        )
        if self.vm_ip:
            self.vm_ip_id = CmdbHostLogicserver.get_ip_id(ip_dict)

    def format_para(self):
        data_dict = dict(
            order_id=self.order_id,
            tenant_id=self.tenant_id,
            task_id=self.com_async_task_id,
            target_address=self.target_address,
            address_id=self.address_id
        )
        return data_dict