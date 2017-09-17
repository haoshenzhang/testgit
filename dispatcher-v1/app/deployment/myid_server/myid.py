# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
import requests
from flask import g , current_app
from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus
from app.order.models import DisOrderLog
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
from app.utils import client
from app.utils import helpers
from app.configs.api_uri import operation as op
from app.order.services import DisOrderService, DisOrderLogService


class MyIdBuildParm(BaseBuildParm):
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class AllocMyId(BaseAlloc):
    """
    分配my_id
    返回的数据格式：
    """
    def __init__(self, data, oder_id):
        self.order_id = data['id']
        self.vpc_id = data['ip_alloc_info']['vpc_id']
        self.custom_pool_id = helpers.json_loads(data['apply_info'])['pool_id']
        self.formated_parm =  helpers.json_dumps(self.format_para())
        self.g_dict = self.format_para()

    def format_para(self):
        return dict(
            vpc_id=self.vpc_id,
            custom_pool_id=self.custom_pool_id
        )

    def compute(self):
        myid_info_uri = op.get_full_uri(op.ALLOC_MYID_URI)
        current_app.logger.info(u"分配Myid URL:" + myid_info_uri)
        current_app.logger.info(u"分配Myid POST DATA:" + self.formated_parm)
        log = dict(
            operation_name=u'alloc_myid',
            operation_object=u'myid',
            execution_status=u'doing',
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)
        status, data, content = g.request(
            uri=myid_info_uri + '?vpc_id=%s&custom_pool_id=%s'
                                  % (self.g_dict['vpc_id'], self.g_dict['custom_pool_id']), method='get')
        current_app.logger.info(u"Myid分配结果:{}".format(content))
        if content['status'] == '10000':
            log['execution_status'] = OrderStatus.succeed
            DisOrderLogService.created_order_log(log)
            myid_info = dict(Myid_alloc_info = content['data'])
            return myid_info
        if content['status'] != '10000':
            log['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(log)
            return None


class MyIdWorker(BaseWorker):
    def start_work(self):
        self.order_serial_num = DisOrderService.get_order_details(self.order_id, field='serial_number')
        self.alloc_data = helpers.json_loads(ProcessMappingTask.get_task_data(self.order_id))
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id,u'create_vm')
        self.target_vm = eval(work_list[self.item_no]['execute_parameter'])
        ip_ = self.target_vm.get('ip', None)
        if not ip_:
            ip_ = self.target_vm.get('fixed_ip')
        self.target_item_ip = ip_
        self.formated_parm = helpers.json_dumps(self.format_para())
        self.g_dict = self.format_para()
        current_app.logger.info(u"准备调用安装myid接口")
        current_app.logger.info(u"接口参数为{}".format(self.formated_parm))
        bigeye_create_uri = op.get_full_uri(op.CREATE_MYID_URI)
        current_app.logger.info(u"接口url:{}".format(bigeye_create_uri))
        status, data, content = client.task_request(uri=bigeye_create_uri, body=self.g_dict, method='post',
                                                    app_token=self.app_token)
        current_app.logger.info(u"myid调用结果为:{},{},{}".format(status, data, content))
        order_log_dict = dict(
            order_id=self.order_id,
            operation_object=self.target_vm['hostname']+'-Myid',
            operation_name='my_id',
            execution_status=OrderStatus.doing
        )
        current_app.logger.info(u"插入订单日志")
        DisOrderLogService.created_order_log(order_log_dict)
        self.init_dict['operation_object'] = self.target_vm['hostname']+'-Myid'
        self.init_dict['operation_name'] = 'my_id'
        if content['status'] == '10000':
            current_app.logger.info(u"调用成功")
            self.add_async_task(interval_time=20)
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
            destip=self.target_item_ip,
            hostname=self.target_vm['hostname'],
            name=self.alloc_data['Myid_alloc_info']['name']
        )
        return dict(
            id = self.com_async_task_id,
            order_id = self.order_id,
            data = data_dict
        )