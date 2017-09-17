# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import current_app
from flask import g
from flask import json

from app.utils import helpers

from app.configs.api_uri import operation
from app.deployment.base.base import BaseWorker
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService


class BigeyePolicyUpdate(BaseWorker):
    """
    wei lai
    2017/2/13
    修改bigeye策略
    """

    def update_bigeye_policy(self):
        """
        wei lai
        调用修改bigeye策略接口
        :return:
        """
        # 参数
        order_apply_info = eval(self.order_apply_info)
        task_id = self.com_async_task_id
        order_id = self.order_id
        param = dict()
        param['id'] = task_id
        param['order_id'] = order_id
        data = dict()
        data['param'] = json.dumps(order_apply_info['policy_param'])
        data['job_id'] = order_apply_info['job_id']
        data['bigeye_ip'] = order_apply_info['web_ip']
        data['ip'] = order_apply_info['ip']
        param['data'] = data
        update_bigeye_policy_uri = operation.get_full_uri(operation.ALLOC_BIGEYE_POLICY_URI)
        current_app.logger.info(u"调用修改bigeye策略接口传入参数：{}！".format(helpers.json_dumps(param)))
        status, datas, content = g.request(uri=update_bigeye_policy_uri, method='put', body=helpers.json_dumps(param))
        current_app.logger.info(u"调用修改bigeye策略返回状态：{},结果：{}！".format(status, datas))
        return status

    def start_work(self):
        """
        wei lai
        :return:
        """
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['host_name']
        operation_name = u'update_bigeye_policy'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        status = BigeyePolicyUpdate.update_bigeye_policy(self)
        if status:
            self.add_async_task(20)
            current_app.logger.info(u"启动异步任务，修改bigeye策略！")
            return True, 'start work'
        else:
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict)
            return None