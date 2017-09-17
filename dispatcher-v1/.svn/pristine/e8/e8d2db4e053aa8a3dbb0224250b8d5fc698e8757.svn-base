# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask import current_app

from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
import requests

from app.order.constant import OrderStatus
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
from app.configs.api_uri import network,operation as op
from app.utils import helpers,client
from app.order.services import DisOrderService, DisOrderLogService
from app.cmdb.vm.models import CmdbHostLogicserver
import json
from flask import g

class VpnPolicyBuildParm(BaseBuildParm):
    """
    daiguanlin@126.com
    创建vpn策略
    """
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class VpnPolicyWorker(BaseWorker):
    """
    daiguanlin@126.com
    创建vpn策略
    """
    #todo 直接update_task , self.task_info
    def start_work(self):
        self.pre()
        if self.safety_flag == 0:
            order_details = DisOrderService.get_order_details(self.order_id)
            self.tenant_id = order_details['tenant_id']
            resource_type = order_details['resource_type']
            current_app.logger.info(u"开始分配vpn策略")
            order_log_dict = dict(
                order_id=self.order_id,
                operation_object='VPN',
                operation_name=u'vpn_policy',
                execution_status=OrderStatus.doing
            )
            self.init_dict = order_log_dict
            if resource_type == 'PM' or resource_type == 'PM_Cluster':
                current_app.logger.info(u"分配物理机vpn策略")
                DisOrderLogService.created_order_log(order_log_dict)
                data = json.loads(self.data)
                for i in data['ip_alloc_info']['ip']:
                    ip = i['addr']
                    ip_id = i['id']
                    self.address_id = ip_id
                    self.target_address = ip
                    self.g_dict = self.format_para()
                    self.formated_parm = helpers.json_dumps(self.format_para())
                    vpn_policy_uri = network.get_full_uri(network.CREATE_VPN)
                    current_app.logger.info(u"准备调用vpn policy接口：")
                    current_app.logger.info(u"接口地址为:"+vpn_policy_uri)
                    current_app.logger.info(u"请求参数为:"+self.formated_parm)
                    status, data, content = client.task_request(uri=vpn_policy_uri,body=self.g_dict, method='put', app_token=self.app_token)
                    if status:
                        current_app.logger.info(u"调用接口成功")
                        self.add_async_task(interval_time=20)
                        return True, 'start work'
                    else:
                        order_log_dict['execution_status'] = OrderStatus.failure
                        DisOrderLogService.created_order_log(order_log_dict)
                        current_app.logger.info(content)
                        current_app.logger.info(data)
                        current_app.logger.info(u"调用接口失败")
                        current_app.logger.info(status)
                        return None
            else:
                self.tenant_id = DisOrderService.get_order_details(self.order_id, 'tenant_id')
                current_app.logger.info(u"开始为虚机分配vpn策略")
                alloc_data = ProcessMappingTask.get_task_data(self.order_id)
                alloc_data = json.loads(alloc_data)
                self.virtual_type = None
                if 'virtual_type' in alloc_data:
                    self.virtual_type = alloc_data['virtual_type']
                work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id, 'create_vm')
                target_item_info = eval(work_list[self.item_no]['execute_parameter'])
                self.target_address = None
                if self.virtual_type == 'VMware' or self.virtual_type == None:
                    self.target_address = target_item_info['ip']
                if self.virtual_type == 'Openstack':
                    self.target_address = target_item_info['floating_ip']
                tem_dict = dict(
                    addr=self.target_address
                )
                self.address_id = CmdbHostLogicserver.get_ip_id(tem_dict)
                self.g_dict = self.format_para()
                self.formated_parm = helpers.json_dumps(self.format_para())
                vpn_policy_uri = network.get_full_uri(network.CREATE_VPN)
                current_app.logger.info(u"准备调用vpn policy接口：")
                current_app.logger.info(u"接口地址为:{}".format(vpn_policy_uri))
                current_app.logger.info(u"请求参数为:{}".format(self.formated_parm))
                order_log_dict = dict(
                    order_id=self.order_id,
                    operation_object=str(self.address_id),
                    operation_name='vpn_policy',
                    execution_status=OrderStatus.doing
                )
                current_app.logger.info(u"插入订单日志")
                self.init_dict['operation_object'] = str(self.address_id)
                self.init_dict['operation_name'] = 'vpn_policy'
                DisOrderLogService.created_order_log(order_log_dict)
                status, data, content = client.task_request(uri=vpn_policy_uri, body=self.g_dict, method='put',
                                                            app_token=self.app_token)
                current_app.logger.info(u"调用完成")
                if status:
                    current_app.logger.info(u"调用接口成功")
                    self.add_async_task(interval_time=20)
                    return True, 'start work'

                else:
                    order_log_dict['execution_status'] = OrderStatus.failure
                    DisOrderLogService.created_order_log(order_log_dict)
                    current_app.logger.info(content)
                    current_app.logger.info(data)
                    current_app.logger.info(u"调用接口失败")
                    current_app.logger.info(status)
                    return None
        if self.safety_flag == 1:
            current_app.logger.info(u"内部租户,跳过vpn 策略")
            from app.process.task import TaskService
            import threading
            thread_ = threading.Thread(target=VpnPolicyWorker.finish_work_,args=(self.order_id, self.task_info, "FINISH",
                                                                                "no VPN",self.init_dict,self.com_async_task_id))
            thread_.start()
            return True, 'start work'

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
        import time
        time.sleep(5)
        current_app.logger.info('准备完成节点')
        TaskService.update_task(order_id, task_info, com_async_task_status, com_async_task_result,com_async_task_id,
                                operation_object=operation_object, operation_name=operation_name)
        ctx.pop()

    def pre(self):
        apply_info = json.loads(self.order_apply_info)
        self.safety_flag = apply_info.get('safety_flag',0)

    def format_para(self):
        data_dict = dict(
            order_id = self.order_id,
            tenant_id=self.tenant_id,
            task_id = self.com_async_task_id,
            target_address = self.target_address,
            address_id = self.address_id
        )
        return data_dict