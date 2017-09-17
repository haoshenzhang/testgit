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

from app.utils.format import format_result


class RemoveVpnPolicyBuildParm(BaseBuildParm):
    """
    daiguanlin@126.com
    创建vpn策略
    """
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class RemoveVpnPolicyWorker(BaseWorker):
    """
    daiguanlin@126.com
    移除vpn策略
    """
    def start_work(self):
        self.pre()
        if self.safety_flag == 0:
            current_app.logger.info(u"准备移除VPN策略")
            apply_info = json.loads(self.order_apply_info)
            order_details = DisOrderService.get_order_details(self.order_id)
            self.tenant_id = order_details['tenant_id']
            vm_id_list = apply_info['vm_id_list']
            vm_id_list = vm_id_list.split(',')
            vm_id = vm_id_list[self.item_no]
            self.vm_vpn_info = CmdbHostLogicserver.get_vm_vpn_info(vm_id)
            self.vm_vpn_info = format_result(self.vm_vpn_info)[0]
            self.g_dict = self.format_para()
            self.formated_parm = helpers.json_dumps(self.format_para())
            vpn_policy_uri = network.get_full_uri(network.CREATE_VPN)
            order_log_dict = dict(
                order_id=self.order_id,
                operation_object=str(self.vm_vpn_info['id']),
                operation_name='rm_vpn_policy',
                execution_status=OrderStatus.doing
            )
            current_app.logger.info(u"插入订单日志")
            self.init_dict['operation_object'] = str(self.vm_vpn_info['id'])
            self.init_dict['operation_name'] = 'rm_vpn_policy'
            DisOrderLogService.created_order_log(order_log_dict)
            status, data, content = client.task_request(uri=vpn_policy_uri, body=self.g_dict, method='delete',
                                                        app_token=self.app_token)
            if status:
                current_app.logger.info(u"调用移除vpn policy成功")
                self.add_async_task(interval_time=20)
                return True, 'start work'
            else:
                order_log_dict['execution_status'] = OrderStatus.failure
                current_app.logger.info(u"content,{}".format(content))
                DisOrderLogService.created_order_log(order_log_dict)
                current_app.logger.info(u"调用移除vpn policy失败")
                return None

        if self.safety_flag == 1:
            current_app.logger.info(u"内部租户,跳过vpn 策略")
            from app.process.task import TaskService
            import threading
            thread_ = threading.Thread(target=RemoveVpnPolicyWorker.finish_work_,args=(self.order_id, self.task_info, "FINISH",
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
        print operation_object,operation_name
        TaskService.update_task(order_id, task_info, com_async_task_status, com_async_task_result,com_async_task_id,
                                operation_object=operation_object, operation_name=operation_name)
        ctx.pop()

    def pre(self):
        apply_info = json.loads(self.order_apply_info)
        self.safety_flag = apply_info.get('safety_flag', 0)

    def format_para(self):
        data_dict = dict(
            order_id = self.order_id,
            tenant_id=self.tenant_id,
            task_id = self.com_async_task_id,
            target_address = self.vm_vpn_info['addr'],
            address_id = self.vm_vpn_info['id']
        )
        return data_dict