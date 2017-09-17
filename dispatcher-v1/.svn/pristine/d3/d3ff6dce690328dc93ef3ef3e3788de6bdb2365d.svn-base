# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import g

from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
import requests

from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
from app.configs.api_uri import operation as op
from app.utils import client
from app.utils import helpers
from flask import current_app
from app.order.services import DisOrderService, DisOrderLogService


class BigEyeScriptBuildParm(BaseBuildParm):
    """
    daiguanlin@126.com
    bigeye布脚本处理返回值类
    """
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class BigEyeScriptWorker(BaseWorker):
    """
    daiguanlin@126.com
    bigeye安装脚本worker类
    """
    def start_work(self):
        self.task_para = ProcessMappingTask.get_task_info(self.order_id)
        for i in self.task_para['BigEyePolicy']:
            i['cron'] = "0 0/2 * * * ?"
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id,'create_vm')
        target_item_info = eval(work_list[self.item_no]['execute_parameter'])
        ip_ = target_item_info.get('ip',None)
        if not ip_:
            ip_ = target_item_info.get('fixed_ip')
        self.target_item_ip = ip_
        bigeye_alloc_data = ProcessMappingTask.get_task_info(self.order_id)
        self.bigeye_ip = bigeye_alloc_data['Bigeye_alloc_info']['bigeye_ip']
        self.g_dict = self.format_para()
        bigeye_script_create_uri = op.get_full_uri(op.CREATE_BIGEYE_SCRIPT_URI)
        current_app.logger.info(u"调用bigeye_script_create_uri接口{}:".format(bigeye_script_create_uri))
        current_app.logger.info(bigeye_script_create_uri)
        current_app.logger.info(u"请求参数为{}".format(self.g_dict))
        current_app.logger.info(self.g_dict)
        status, data, content = client.task_request(uri=bigeye_script_create_uri, body=self.g_dict, method='post',
                                                    app_token=self.app_token)
        current_app.logger.info(u"Bigeye脚本调用结果为:{},{},{}".format(status, data, content))
        order_log_dict = dict(
            order_id=self.order_id,
            operation_object=target_item_info['hostname']+'-bigeye_script',
            operation_name='bigeye_script',
            execution_status=OrderStatus.doing
        )
        current_app.logger.info(u"插入订单日志")
        self.init_dict['operation_object'] = target_item_info['hostname']+'-bigeye_script'
        self.init_dict['operation_name'] = 'bigeye_script'
        DisOrderLogService.created_order_log(order_log_dict, commit=True)
        if content['status'] == u'10000':
            self.add_async_task(interval_time=20)
            return True, 'start work'
        else:
            order_log_dict['execution_status'] = OrderStatus.failure
            DisOrderLogService.created_order_log(order_log_dict)
            ComAsyncTask.del_com_task(self.com_async_task_id)
            return None

    def pre(self):
        pass

    def format_para(self):
        data_dict = dict(
            policy = self.task_para['BigEyePolicy'],
            ip = self.target_item_ip,
            bigeye_ip = self.bigeye_ip
        )
        return dict(
            id=self.com_async_task_id,
            order_id=self.order_id,
            data=data_dict
        )