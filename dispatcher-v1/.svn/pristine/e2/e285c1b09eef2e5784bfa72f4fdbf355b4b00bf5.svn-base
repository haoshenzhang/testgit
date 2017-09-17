# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
daiguanlin
"""
from app.deployment.base.base import BaseWorker
from app.configs.api_uri.infrastructure import VM_DELETE_URI, OP_DELETE_URI
from app.order.constant import OrderStatus
from app.order.services import DisOrderLogService
from app.utils import helpers
from app.configs.api_uri import infrastructure
import json
from app.cmdb.vm.models import CmdbHostLogicserver
from app.utils.format import format_result
from app.catalog.vmhost.models import Tenant_Openstack_Ref
from flask import g, current_app


class VMDeleteWorker(BaseWorker):
    """
    虚机操作worker类
    """
    def start_work(self):
        self.apply_info = json.loads(self.order_apply_info)
        vm_id_list_ = self.apply_info['vm_id_list']
        vm_id_list = vm_id_list_.split(',')
        self.vm_id = vm_id_list[self.item_no]
        vm_info = CmdbHostLogicserver.vm_detail_by_id(uuid=self.vm_id)
        self.vm_info = format_result(vm_info)[0]
        self.hypervisor_type = self.vm_info['hypervisor_type']
        self.vm_name = self.vm_info['name']
        self.pre()
        self.g_dict = self.format_para()
        self.formated_parm = helpers.json_dumps(self.format_para())
        self.init_dict['operation_object'] = self.vm_name
        self.init_dict['operation_name'] = u'delete'
        if self.hypervisor_type == 'VMware':
            current_app.logger.info(u"准备删除接口VMware")
            vmware_action_uri = infrastructure.get_full_uri(VM_DELETE_URI)
            current_app.logger.info(u"vmware接口url" + vmware_action_uri)
            status,data,content = g.request(uri=vmware_action_uri,body=self.g_dict,method='delete')
            #status, data, content = g.request(uri=vmware_action_uri + '?cluster_id=%s&server_id=%s&action=delete&task_id=%s'
            #                                                           % (self.g_dict['cluster_id'], self.g_dict['server_id'],
            #                                                              self.g_dict['task_id']),method='delete')
            if content['status'] == '10000':
                current_app.logger.info(u"调用删除虚机接口成功")
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=self.vm_name,
                    operation_name=u'delete',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)

                self.add_async_task(interval_time=20)
                args_dict = dict(
                    status='deleting',
                    internal_id=self.vm_id
                )
                CmdbHostLogicserver.update_vm_status(args_dict)
                return True, 'start work'
            else:
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=self.vm_name,
                    operation_name=u'delete',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                order_log_dict['execution_status'] = OrderStatus.failure
                DisOrderLogService.created_order_log(order_log_dict)
                current_app.logger.info(u"调用删除虚机接口失败")
                return None

        if self.hypervisor_type == 'Openstack':
            current_app.logger.info(u"准备调用删除接口Openstack")
            openstack_action_uri = infrastructure.get_full_uri(OP_DELETE_URI)
            current_app.logger.info(u"openstack接口url"+openstack_action_uri)
            status, data, content = g.request(uri=openstack_action_uri, body=self.g_dict, method='delete')
            #status, data, content = g.request(
            #    uri=openstack_action_uri + '?project_id=%s&server_id=%s&az_id=%s&task_id=%s'
            #                            % (self.g_dict['project_id'], self.g_dict['server_id'],self.g_dict['az_id'],
            #                               self.g_dict['task_id']), method='delete')
            if content['status'] == '10000':
                current_app.logger.info(u"调用删除虚机接口成功")
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object='VM',
                    operation_name=u'delete',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                self.add_async_task(interval_time=20)
                args_dict = dict(
                    status='deleting',
                    internal_id=self.vm_id
                )
                CmdbHostLogicserver.update_vm_status(args_dict)
                return True, 'start work'
            else:
                current_app.logger.info(u"调用删除虚机接口失败")
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=self.vm_name,
                    operation_name=u'delete',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                DisOrderLogService.created_order_log(order_log_dict)
                order_log_dict['execution_status'] = OrderStatus.failure
                DisOrderLogService.created_order_log(order_log_dict)
                return None


    def pre(self):
        self.physic_pool_id = int(self.vm_info['physic_pool_id'])
        if self.hypervisor_type == 'Openstack':
            self.logic_pool_id = self.vm_info['logicpool_id']
            tenant_id = g.tenant['tenant_id']
            tenant_ref_info = Tenant_Openstack_Ref.get_project_id_by_teannt(self.logic_pool_id,tenant_id)
            tenant_ref_info = format_result(tenant_ref_info)[0]
            self.project_id = tenant_ref_info['project_id']

    def format_para(self):
        if self.hypervisor_type == 'VMware':
            return dict(
                cluster_id = self.physic_pool_id,
                server_id = self.vm_id,
                action = u'delete',
                task_id = self.com_async_task_id
            )
        if self.hypervisor_type == 'Openstack':
            return dict(
                project_id = self.project_id,
                server_id = self.vm_id,
                az_id = self.physic_pool_id,
                task_id = self.com_async_task_id
            )