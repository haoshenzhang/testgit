# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
from flask import current_app
from flask import g

from app.catalog.vmhost.models import Tenant_Openstack_Ref
from app.catalog.vmhost.services import VMService
from app.deployment.base.base import BaseWorker
from app.configs.api_uri.infrastructure import VM_ACTION_URI, OP_ACTION_URI
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService
from app.utils import helpers
from app.configs.api_uri import infrastructure
import json
from app.cmdb.vm.models import CmdbHostLogicserver
from app.utils.format import format_result


class VMActionWorker(BaseWorker):
    """
    虚机操作worker类
    """
    def start_work(self):
        self.apply_info = json.loads(self.order_apply_info)
        vm_id_list_ = self.apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        self.vm_id = vm_id_list[self.item_no]
        args = dict(
            vm_id=self.vm_id
        )
        vm_info = VMService.get_vm_info(args)
        self.hypervisor_type = vm_info[0]['hypervisor_type']
        self.vm_name = vm_info[0]['name']
        addr_args = dict(
            internal_id = self.vm_id
        )
        addr = CmdbHostLogicserver.get_vm_vpn_info(self.vm_id)
        self.vm_ip_info = format_result(addr)[0]
        self.vm_ip = self.vm_ip_info['addr']
        self.action = self.apply_info['action']
        self.pre()
        self.g_dict = self.format_para()
        self.formated_parm = helpers.json_dumps(self.format_para())
        self.init_dict['operation_object'] = self.vm_name
        self.init_dict['operation_name'] = self.action
        if self.hypervisor_type == 'VMware':
            current_app.logger.info(u"准备调用虚机action接口,vmware")
            vmware_action_uri = infrastructure.get_full_uri(VM_ACTION_URI)
            status, data, content = g.request(uri=vmware_action_uri, body=self.g_dict, method='post')
            if content['status'] == '10000':
                current_app.logger.info(u"虚机action接口调用成功,vmware")
                args_dict = None
                if self.action == 'stop':
                    args_dict = dict(
                        status='stopping',
                        internal_id=self.vm_id
                    )
                if self.action == 'start':
                    args_dict = dict(
                        status='starting',
                        internal_id=self.vm_id
                    )
                if self.action == 'reboot':
                    args_dict = dict(
                        status='restarting',
                        internal_id=self.vm_id
                    )
                self.add_async_task(interval_time=20)
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=self.vm_name,
                    operation_name=self.action,
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)

                CmdbHostLogicserver.update_vm_status(args_dict)
                return True, 'start work'
            else:
                current_app.logger.info(u"虚机action接口调用失败")
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
            current_app.logger.info(u"准备调用虚机action接口,openstack")
            openstack_action_uri = infrastructure.get_full_uri(OP_ACTION_URI)
            status, data, content = g.request(uri=openstack_action_uri, body=self.g_dict, method='post')
            if content['status'] == '10000':
                args_dict = None
                if self.action == 'stop':
                    args_dict = dict(
                        status='stopping',
                        internal_id=self.vm_id
                    )
                if self.action == 'start':
                    args_dict = dict(
                        status='starting',
                        internal_id=self.vm_id
                    )
                if self.action == 'reboot':
                    args_dict = dict(
                        status='restarting',
                        internal_id=self.vm_id
                    )
                current_app.logger.info(u"虚机action接口调用成功,openstack")
                self.add_async_task(interval_time=20)
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=self.vm_name,
                    operation_name=self.action,
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                CmdbHostLogicserver.update_vm_status(args_dict)
                return True, 'start work'
            else:
                current_app.logger.info(u"虚机action接口调用失败")
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

    def pre(self):
        vm_info = CmdbHostLogicserver.vm_detail_by_id(uuid=self.vm_id)
        vm_info = format_result(vm_info)[0]
        vm_id = vm_info['internal_id']
        tenant_id = g.tenant['tenant_id']
        if self.hypervisor_type == 'VMware':
            self.clster_id = int(vm_info['physic_pool_id'])
        if self.hypervisor_type == 'Openstack':
            self.logic_pool_id = vm_info['logicpool_id']
            tenant_ref_info = Tenant_Openstack_Ref.get_project_id_by_teannt(self.logic_pool_id, tenant_id)
            tenant_ref_info = format_result(tenant_ref_info)[0]
            self.project_id = tenant_ref_info['project_id']
            self.physic_pool_id = vm_info['pm_cluster_id']

    def format_para(self):
        if self.hypervisor_type == 'VMware':
            return dict(
                cluster_id = self.clster_id,
                server_id = self.vm_id,
                action = self.action,
                task_id = self.com_async_task_id,
                ip = self.vm_ip
            )

        if self.hypervisor_type == 'Openstack':
            return dict(
                az_id = self.physic_pool_id,
                project_id=self.project_id,
                server_id = self.vm_id,
                action = self.action,
                task_id = self.com_async_task_id
            )