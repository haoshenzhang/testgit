# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
安全服务项与租户关联
"""
from flask import current_app

from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrder
from app.order.services import DisOrderLogService
from app.security.member.services import SecurityService


class SecurityTenantRef(BaseWorker):

    def start_work(self):
        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        com_async_task_id = self.com_async_task_id
        from app.process.models import ProcessMappingTaskItem
        ProcessMappingTaskItem.update_status('running', order_id, task_info['id'], 'waiting')
        # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['name_en']
        operation_name = u'create_tenant_security_services'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        com_async_task_status = u'FINISH'
        # 完成节点，增加安全服务的关联关系
        ss = SecurityService.insert_tenant_security(order_apply_info, commit=True)
        if ss:
            # 增加订单与资源的关系
            for i in order_apply_info['security_services_id'] .split(','):
                order_res = dict()
                order_res['resource_id'] = i
                order_res['order_id'] = order_id
                order_res['resource_type'] = ResourceType.SECURITY_SERVICES.value
                DisOrder.insert_order_ref(order_res)
            result = order_apply_info['security_services_id']
            self.add_async_task(20)
            current_app.logger.info(u"起动关联服务项节点异步任务成功！")
            import threading
            thread_ = threading.Thread(target=SecurityTenantRef.update_task_status,
                                       args=(self.com_async_task_id, "FINISH", 1,))
            thread_.start()
            return True, 'start work'
        else:
            com_async_task_status = u'failed'
            result = u'failed'
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            # ComAsyncTask.del_com_task(com_async_task_id)
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            return None

    @staticmethod
    def update_task_status(task_id, status, code):
        """
        :param task_id:
        :param status:
        :param code:
        :return:
        """
        from app.extensions import back_ground_scheduler
        ctx = back_ground_scheduler.app.app_context()
        ctx.push()
        ComAsyncTask.update_async_task_status(task_id, status, code)
        current_app.logger.info(u"修改com_task表中的状态成功！")
        ctx.pop()