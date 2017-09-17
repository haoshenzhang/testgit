# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
bigeye 监控services
"""
from flask import current_app
from flask import g
from flask import json

from app.catalog.bigeye_policy.models import OprBigeyePolicy, OprHostBigeyeRef
from app.cmdb.vm.models import CmdbHostLogicserver
from app.order.constant import ResourceType
from app.order.models import DisOrder
from app.order.services import DisOrderService
from app.utils.format import format_result


class BigeyePolicyServices(object):
    """
    bigeye services
    """
    @staticmethod
    def get_policy_by_id(host_id):
        """
        通过主机id查询监控内容
        :param host_id: 策略名称
        :return:
        """
        policy = OprBigeyePolicy.get_policy_by_id(host_id)
        policy = format_result(policy)
        if policy:
            for i in policy:
                # i['default_policy_param'] = json.loads(i['default_policy_param'])
                i['param'] = i['param'].replace("None", "null")
                i['param'] = json.loads(i['param'])
        return policy

    @staticmethod
    def update_policy_by_id(args):
        """
         修改虚机的policy （关系表中）
        :param args: 策略名称
        :return:
        """
        # 查询job_id根据虚机id及策略id
        application_id = args['application_id']
        host_id = args['host_id']
        policy_id = args['policy_id']
        host_name = args['host_name']
        policy = OprHostBigeyeRef.get_job_ip_id(host_id, policy_id)
        policy = format_result(policy)
        job_id = policy[0]['job_id']
        bigeye_ip = policy[0]['ip_addr']
        ip_id = CmdbHostLogicserver.get_ip_id_by_ref(host_id)
        ip_args = dict(
            id = ip_id
        )
        ip = CmdbHostLogicserver.get_ip_by_ip_id(ip_args)

        # 1.生成订单 2.生成流程 3.成功后修改关系表
        param = dict()
        param['application_id'] = application_id
        param['resource_type'] = ResourceType.Bigeye_policy.value
        param['operation_type'] = u'update'
        param['user_id'] = g.user['current_user_id']
        param['tenant_id'] = g.tenant['tenant_id']
        apply_info = dict()
        apply_info['host_id'] = host_id
        apply_info['host_name'] = host_name
        apply_info['policy_id'] = policy_id
        apply_info['job_id'] = job_id
        apply_info['web_ip'] = bigeye_ip
        apply_info['ip'] = ip
        apply_info['policy_param'] = args['param']
        param['apply_info'] = apply_info
        order_id, serial_number = DisOrderService.create_order(param, commit = True)
        current_app.logger.info(u"生成订单参数:{}，订单id：{}".format(param, order_id))
        # 2.调用流程
        from app.process.task import TaskService
        result1 = TaskService.create_task(order_id)
        current_app.logger.info(u"创建编排:{}".format(result1[1]))
        if result1[0] and result1[1] == '成功':
            result2 = TaskService.start_task(order_id, 0)
            current_app.logger.info(u"开始编排流程:{}".format(result2[1]))
            if result2[0]:
                current_app.logger.info(u"修改策略正在执行")
                return True, serial_number
            else:
                current_app.logger.info(u"修改策略失败")
                return False, serial_number
