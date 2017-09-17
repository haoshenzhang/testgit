# !/usr/bin/python
# -*- coding: utf-8 -*-
import time

from flask import current_app
from flask import g

from app.configs.api_uri import infrastructure
from app.utils import helpers
from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService
from app.process.models import ProcessMappingTaskItem


class CreateProject(BaseWorker):

    @staticmethod
    def create_project(order_apply_info):
        """
        创建openstack中的project
        """
        logic_pool_id = order_apply_info['pool_id']
        tenant_name = order_apply_info['tenant_name']
        args = dict()
        args['tenant_name'] = tenant_name
        args['logic_pool_id'] = logic_pool_id
        uri = infrastructure.get_full_uri(infrastructure.CREATE_OPENSTACK_PROJECT)
        status, datas, content = g.request(uri=uri, method='post', body=helpers.json_dumps(args))
        if status:
            current_app.logger.info(u"调用infrastructure平台，在openstack建租户，返回结果:{}！".format(datas))
            return datas['id']
        else:
            current_app.logger.info(u"调用infrastructure平台，失败，返回结果:{}！".format(datas))
            return False

    def start_work(self):
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        com_async_task_id = self.com_async_task_id
        ProcessMappingTaskItem.update_status('running', order_id, task_info['id'], 'waiting')
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['tenant_name']
        operation_name = u'create_openstack_tenant_project'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        project_id = CreateProject.create_project(order_apply_info)
        if project_id:
            com_async_task_status = u'FINISH'
            ComAsyncTask.update_async_task_status(com_async_task_id, 'FINISH', 1)
            result = project_id
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict)
            # 再次创建订单日志（完成）
            # execution_status = OrderStatus.succeed
            # args['execution_status'] = execution_status
            # DisOrderLogService.created_order_log(args, commit=True)
            return True, 'start work'
        else:
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict)
            # 再次创建订单日志（完成）
            # execution_status = OrderStatus.failure
            # args['execution_status'] = execution_status
            # DisOrderLogService.created_order_log(args, commit=True)
            return None
