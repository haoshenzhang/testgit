# !/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
from app.deployment.bigeye_server.models import Bigeye
from app.deployment.models import ComAsyncTask
from app.management.image.models import DisOsTemplate
from app.management.logicpool.models import InfLogicPool
from app.order.constant import OrderStatus
from app.order.models import DisOrderLog
from app.order.services import DisOrderLogService, DisOrderService
from app.process.models import ProcessMappingTask,ProcessMappingTaskItem
from app.utils import client
from app.utils import helpers
from app.configs.api_uri import operation as op
from flask import g, current_app

from app.utils.format import format_result


class BigEyePBuildParm(BaseBuildParm):
    """
    daiguanlin@126.com
    bigeye处理返回data的类
    """
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result


class GetBigEye(BaseAlloc):
    """
    daiguanlin@126.com
    分配bigeye的类
    """
    def __init__(self, data, order_id):
        self.vpc_id = data['ip_alloc_info']['vpc_id']
        self.order_id = order_id
        self.custom_pool_id = int(helpers.json_loads(data['apply_info'])['pool_id'])
        order_apply_info = DisOrderService.get_order_details(order_id, 'apply_info')
        order_apply_info = json.loads(order_apply_info)
        self.templateId = int(order_apply_info['template_id'])
        args = dict(
            id=self.templateId
        )
        template_info =Bigeye.get_os_type(args)
        template_info = format_result(template_info)[0]
        os_type = template_info['os_type']
        if os_type == 'Windows':
            self.os_type = 'Windows'
        else:
            self.os_type = 'Linux'
        self.g_dict = self.format_para()
        self.formated_parm = helpers.json_dumps(self.format_para())

    def format_para(self):
        return dict(
            vpc_id=self.vpc_id,
            custom_pool_id=self.custom_pool_id
        )

    def compute(self):
        bigeye_info_uri = op.get_full_uri(op.ALLOC_BIGEYE_URI)
        bigeye_policy_uri = op.get_full_uri(op.ALLOC_BIGEYE_POLICY_URI)
        current_app.logger.info(u"分配Bigeye server URL:".format(bigeye_info_uri))
        current_app.logger.info(u"分配Bigeye policy URL:".format(bigeye_policy_uri))
        current_app.logger.info(u"分配Bigeye POST DATA:".format(self.formated_parm))
        log = dict(
            operation_name=u'alloc_bigeye',
            operation_object=u'bigeye_server',
            execution_status=OrderStatus.doing,
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)
        status, data, content = g.request(
            uri=bigeye_info_uri, method='get')
        status_policy, data_policy, content_policy = g.request(
            uri=bigeye_policy_uri + '?type=%s'
                                  % (self.os_type), method='get')
        if content['status'] == '10000' and content_policy['status'] == '10000':
            log['execution_status'] = OrderStatus.succeed
            DisOrderLogService.created_order_log(log)
            bigeye_info = dict(Bigeye_alloc_info=content['data'],BigEyePolicy=content_policy['data'])
            return bigeye_info
        else:
            log['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(log)
            return None

class BigEyeWorker(BaseWorker):
    """
    daiguanlin@126.com
    安装bigeye的worker类
    """
    def start_work(self):
        self.alloc_data = ProcessMappingTask.get_task_data(self.order_id)
        self.alloc_data = helpers.json_loads(self.alloc_data)['Bigeye_alloc_info']
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id, 'create_vm')
        self.target_vm = work_list[self.item_no]['execute_parameter']
        self.target_vm = eval(self.target_vm)
        self.g_dict = self.format_para()
        self.formated_parm = helpers.json_dumps(self.format_para())
        bigeye_create_uri = op.get_full_uri(op.CREATE_BIGEYE_URI)
        current_app.logger.info(u"调用bigeye_server接口:{}".format(bigeye_create_uri))
        current_app.logger.info(self.formated_parm)
        status, data, content = client.task_request(uri=bigeye_create_uri, body=self.g_dict, method='post',
                                                    app_token=self.app_token)
        current_app.logger.info(u"bigeye-server调用结果为:{},{},{}".format(status,data,content))
        order_log_dict = dict(
            order_id=self.order_id,
            operation_object=self.target_vm['hostname']+'-bigeye',
            operation_name='bigeye_server',
            execution_status=OrderStatus.doing
        )
        current_app.logger.info(u"插入订单日志")
        self.init_dict['operation_object'] =self.target_vm['hostname']+'-bigeye'
        self.init_dict['operation_name'] = 'bigeye_server'
        DisOrderLogService.created_order_log(order_log_dict, commit=True)
        if content['status'] == '10000':
            self.add_async_task(interval_time=35)
            return True, 'start work'
        else:
            order_log_dict['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(order_log_dict)
            ComAsyncTask.del_com_task(self.com_async_task_id)
            return None

    def format_para(self):
        data_dict = dict(
            bigeye_ip=self.alloc_data['bigeye_ip'],
            agent_version=self.alloc_data['agent_version'],
            ms_server_list=self.alloc_data['ms_server_list'],
            server_port=self.alloc_data['server_port'],
            ip=self.target_vm['ip'],
            host_name=self.target_vm['hostname'],
            username=u"root",
            password=self.target_vm['password']
        )
        return dict(
            id=self.com_async_task_id,
            order_id=self.order_id,
            data=data_dict
        )