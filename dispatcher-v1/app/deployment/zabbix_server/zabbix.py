# !/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests
from flask import g,current_app
from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus
from app.order.models import DisOrderLog
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
from app.utils import client
from app.utils import helpers
from app.configs.api_uri import operation as op
from app.order.services import DisOrderService, DisOrderLogService


class ZabbixBuildParm(BaseBuildParm):
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class AllocZabbix(BaseAlloc):
    """
    分配my_id
    返回的数据格式：
    """
    def __init__(self, data, oder_id):
        self.order_id = data['id']
        self.vpc_id = data['ip_alloc_info']['vpc_id']
        self.custom_pool_id = helpers.json_loads(data['apply_info'])['pool_id']
        self.vpc_id = 0  # 只有0能用
        self.custom_pool_id = 0
        self.g_dict = self.format_para()
        self.formated_parm =  helpers.json_dumps(self.format_para())

    def format_para(self):
        return dict(
            vpc_id=self.vpc_id,
            custom_pool_id=self.custom_pool_id
        )

    def compute(self):
        zabbix_info_uri = op.get_full_uri( op.ALLOC_ZABBIX_URI)
        status, data, content = g.request(
            uri=zabbix_info_uri + '?vpc_id=%s&custom_pool_id=%s'
                                  % (self.g_dict['vpc_id'], self.g_dict['custom_pool_id']), method='get')
        current_app.logger.info(u"调用分配zabbix接口")
        if content['status'] == '10000':
            log = dict(
                operation_name=u'alloc_zabbix',
                operation_object=u'zabbix_server',
                execution_status=u'doing',
                order_id=self.order_id
            )
            DisOrderLog.created_order_log(log)
            log['execution_status'] = OrderStatus.succeed
            DisOrderLogService.created_order_log(log)
            zabbix_info = dict(Zabbix_alloc_info=content['data'])
            return zabbix_info
        else:
            log = dict(
                operation_name=u'alloc_zabbix',
                operation_object=u'zabbix_server',
                execution_status=OrderStatus.doing,
                order_id=self.order_id
            )
            DisOrderLog.created_order_log(log)
            log['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(log)
            return None


class ZabbixWorker(BaseWorker):
    def start_work(self):
        self.order_serial_num = DisOrderService.get_order_details(self.order_id, field='serial_number')
        self.alloc_data = ProcessMappingTask.get_task_data(self.order_id)
        self.alloc_data = json.loads(self.alloc_data)
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id,'create_vm')
        self.target_vm = work_list[self.item_no]
        self.target_vm = self.target_vm['execute_parameter']
        self.target_vm = eval(self.target_vm)
        self.g_dict = self.format_para()
        self.formated_parm = self.format_para()
        zabbix_create_uri = op.get_full_uri(op.CREATE_ZABBIX_URI)
        current_app.logger.info(u"准备调用安装zabbix接口")
        current_app.logger.info(u"接口参数为")
        current_app.logger.info(self.formated_parm)
        current_app.logger.info(u"接口url为:{}".format(zabbix_create_uri))
        status, data, content = client.task_request(uri=zabbix_create_uri, body=self.g_dict, method='post',
                                                    app_token=self.app_token)
        current_app.logger.info(u"调用结果为,{},{},{}".format(status, data, content))
        order_log_dict = dict(
            order_id=self.order_id,
            operation_object=self.target_vm['hostname'] + '-zabbix',
            operation_name='zabbix',
            execution_status=OrderStatus.doing
        )
        current_app.logger.info(u"插入订单日志")
        self.init_dict['operation_object'] = self.target_vm['hostname'] + '-zabbix'
        self.init_dict['operation_name'] = 'zabbix'
        DisOrderLogService.created_order_log(order_log_dict, commit=True)

        if content['status'] == '10000':
            self.add_async_task(interval_time=40)
            current_app.logger.info(u"调用成功")
            return True, 'start work'
        else:
            order_log_dict['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(order_log_dict)
            ComAsyncTask.del_com_task(self.com_async_task_id)
            current_app.logger.info(u"调用myid接口失败")
            return None

    def pre(self):
        pass

    def format_para(self):
        data_dict = dict(
            hname=self.target_vm['hostname'],
            name=self.alloc_data['Zabbix_alloc_info']['name'],
            zabbixid=self.alloc_data['Zabbix_alloc_info']['id'],
            zabbix_ip=self.alloc_data['Zabbix_alloc_info']['ip'],
            dest_ip=self.target_vm['ip'],
            username='root',
            #password=self.target_vm['password']
            password = '!qaz2wsX'
            #password = '123456'
        )
        return dict(
            id = self.com_async_task_id,
            data = data_dict
        )