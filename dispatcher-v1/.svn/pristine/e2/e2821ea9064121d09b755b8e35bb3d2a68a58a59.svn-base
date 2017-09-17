# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
from flask import current_app
from flask import g

from app.catalog.vmhost.services import VMService
from app.deployment.base.base import BaseWorker
from app.configs.api_uri.infrastructure import VM_ACTION_URI
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService
from app.utils import helpers
from app.configs.api_uri import infrastructure
import json
from app.cmdb.vm.models import CmdbHostLogicserver
from app.utils.format import format_result


class VMRemoveWorker(BaseWorker):
    """
    虚机操作worker类
    """
    def start_work(self):
        self.apply_info = json.loads(self.order_apply_info)
        vm_id_list_ = self.apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        self.vm_id = vm_id_list[self.item_no]
        args = dict(
            vm_id = self.vm_id
        )
        vm_info = VMService.get_vm_info(args)
        self.hypervisor_type = vm_info[0]['hypervisor_type']
        self.vm_status = vm_info[0]['status']
        self.vm_name = vm_info[0]['name']
        self.action = self.apply_info['action']
        self.pre()
        self.g_dict = self.format_para()
        self.formated_parm = helpers.json_dumps(self.format_para())
        self.init_dict['operation_object'] = self.vm_name
        self.init_dict['operation_name'] = self.action
        if self.vm_status == 'running':
            self.init_dict['plug'] = True
            if self.hypervisor_type == 'VMware':
                current_app.logger.info(u"准备请求接口")
                vmware_action_uri = infrastructure.get_full_uri(VM_ACTION_URI)
                current_app.logger.info(u"接口地址为:{}".format(vmware_action_uri))
                status, data, content = g.request(uri=vmware_action_uri, body=self.g_dict, method='post')
                if content['status'] == '10000':
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=self.vm_name,
                        operation_name=self.action,
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    self.add_async_task(interval_time=5)
                    args_dict = dict(
                        status='stopping',
                        internal_id=self.vm_id
                    )
                    CmdbHostLogicserver.update_vm_status(args_dict)
                    return True, 'start work'
                else:
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=self.vm_name,
                        operation_name=self.action,
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    order_log_dict['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(order_log_dict)
                    return None

            if self.hypervisor_type == 'Openstack':
                openstack_action_uri = infrastructure.get_full_uri(VM_ACTION_URI)
                status, data, content = g.request(uri=openstack_action_uri, body=self.g_dict, method='post')
                if content['status'] == '10000':
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=self.vm_name,
                        operation_name=self.action,
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    self.add_async_task(interval_time=5)
                    return True, 'start work'
                else:
                    order_log_dict = dict(
                        order_id=self.order_id,
                        operation_object=self.vm_name,
                        operation_name=self.action,
                        execution_status=OrderStatus.doing
                    )
                    current_app.logger.info(u"插入订单日志")
                    DisOrderLogService.created_order_log(order_log_dict)
                    order_log_dict['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(order_log_dict)
                    return None
        if self.vm_status == 'stopped':
            current_app.logger.info(u"已关机,跳过关机步骤")
            order_log_dict = dict(
                order_id=self.order_id,
                operation_object=self.vm_name,
                operation_name='delete',
                execution_status=OrderStatus.doing
            )
            current_app.logger.info(u"插入订单日志")
            DisOrderLogService.created_order_log(order_log_dict)
            from app.process.task import TaskService
            import threading
            thread_ = threading.Thread(target=VMRemoveWorker.finish_work_,
                                       args=(self.order_id, self.task_info, "FINISH",
                                             "already stopped", self.init_dict,self.com_async_task_id))
            thread_.start()
            return True, 'start work'

    def pre(self):
        vm_info = CmdbHostLogicserver.vm_detail_by_id(uuid=self.vm_id)

        vm_info = format_result(vm_info)[0]
        vm_id = vm_info['internal_id']
        addr_args = dict(
            internal_id=vm_id
        )
        addr = CmdbHostLogicserver.get_vm_vpn_info(vm_id)
        self.vm_ip_info = format_result(addr)[0]
        self.vm_ip = self.vm_ip_info['addr']
        self.clster_id = int(vm_info['physic_pool_id'])

    def format_para(self):
        return dict(
            cluster_id = self.clster_id,
            server_id = self.vm_id,
            ip = self.vm_ip,
            action = 'stop',
            task_id = self.com_async_task_id
        )

    @staticmethod
    def finish_work_(order_id, task_info, com_async_task_status, com_async_task_result, init_dict,com_async_task_id):
        """
        结束轮询最后调用此方法
        :param order_id: 订单id
        :param task_info: dis_process_task_item 中每条item数据
        :param com_async_task_status:  com_async_task 中的status
        :param com_async_task_result: com_async_task 中的result
        :return:
        """
        from app.process.task import TaskService
        from app.extensions import back_ground_scheduler
        ctx = back_ground_scheduler.app.app_context()
        ctx.push()
        operation_object = init_dict.get('operation_object', None)
        operation_name = init_dict.get('operation_name', None)
        operation_name = 'delete'
        import time
        time.sleep(5)
        current_app.logger.info('准备完成节点')
        TaskService.update_task(order_id, task_info, com_async_task_status, com_async_task_result,com_async_task_id,
                                operation_object=operation_object, operation_name=operation_name)
        ctx.pop()