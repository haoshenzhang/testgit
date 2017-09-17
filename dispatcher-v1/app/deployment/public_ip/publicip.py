# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
调用network接口得到可用公网ipID
"""
import time
from flask import current_app
from flask import g
from app.catalog.public_ip.services import PublicIpService
from app.configs.api_uri import network
from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask

from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrder
from app.order.services import DisOrderLogService


class GetPublicIP(BaseWorker):

    @staticmethod
    def get_public_ip(order_apply_info):
        """
        调用network接口
        :return: 可用公网ip的ID
        """
        # 调用接口，传给order_id 和 ip_count
        number = order_apply_info['ip_number']
        order_apply_info['number'] = number
        current_app.logger.info(u"调用network平台，查询空闲公网ip参数:{}！".format(order_apply_info))
        uri = network.get_full_uri(network.Get_FREE_PUBLIC_IP)
        status, datas, content = g.request(uri=uri, method='post', body=order_apply_info)
        current_app.logger.info(u"查询空闲公网ip返回status:{}，datas:{}！".format(status, datas))
        if status:
            current_app.logger.info(u"调用network平台，查询空闲公网ip:{}，返回成功！".format(status))
            return datas
        else:
            current_app.logger.info(u"调用network平台，查询空闲公网ip:{}（可能没有相应ip）！".format(status))
            return status

    def start_work(self):

        order_apply_info = eval(self.order_apply_info)
        order_id = self.order_id
        task_info = self.task_info
        # # 创建订单日志（开始）
        args = dict()
        operation_object = order_apply_info['name_en']
        operation_name = u'bound_tenant_public_ip'
        execution_status = OrderStatus.doing
        self.init_dict['operation_object'] = operation_object
        self.init_dict['operation_name'] = operation_name
        args['operation_object'] = operation_object
        args['operation_name'] = operation_name
        args['execution_status'] = execution_status
        args['order_id'] = order_id
        DisOrderLogService.created_order_log(args, commit=True)
        current_app.logger.info(u"记录订单日志:{}！".format(args))
        ip_ids = GetPublicIP.get_public_ip(order_apply_info)
        if ip_ids:
            # 完成任务，删除记账表，绑定公网ip与租户关系，更改ip状态
            PublicIpService.bound_tenant_ip(order_apply_info, ip_ids, commit=True)
            # 增加订单与资源的关系
            for i in ip_ids:
                resource_id = i['id']
                order_res = dict()
                order_res['order_id'] = order_id
                order_res['resource_type'] = ResourceType.PUBLIC_IP.value
                order_res['resource_id'] = resource_id
                DisOrder.insert_order_ref(order_res)
            self.add_async_task(20)
            current_app.logger.info(u"起动公网ip节点异步任务成功！")
            import threading
            thread_ = threading.Thread(target=GetPublicIP.update_task_status,args=(self.com_async_task_id, "FINISH", 1,))
            thread_.start()
            return True, 'start work'

        else:
            # 再次创建订单日志（失败）
            com_async_task_status = u'failed'
            result = u'failed'
            com_async_task_id  = self.com_async_task_id
            self.init_dict['operation_object'] = operation_object
            self.init_dict['operation_name'] = operation_name
            # ComAsyncTask.del_com_task(com_async_task_id)
            self.finish_work(order_id, task_info, com_async_task_status, result, self.init_dict, com_async_task_id)
            current_app.logger.info(u"调用公网ip接口失败，已修改节点状态，订单状态！")
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


