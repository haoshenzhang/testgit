# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-01-09
    备份策略流程编排
"""
import time

from flask import json, current_app, g

from app.deployment.base.base import BaseWorker
from app.deployment.models import ComAsyncTask
from app.order.constant import OrderStatus
from app.order.models import DisOrder
from app.order.services import DisOrderService, DisOrderLogService
from app.utils.rest_client import RestClient


class BackupPolicy(BaseWorker):

    def add_backup_ticket(self):
        """ 生成工单"""
        apply_info = json.loads(self.order_apply_info)
        order_data = DisOrderService.get_order_details(self.order_id)
        self.init_dict["operation_object"] = apply_info['name']
        self.init_dict['operation_name'] = order_data['operation_type'] + '_backup_policy'
        log = dict()
        log["operation_name"] = self.init_dict['operation_name']
        log["operation_object"] = self.init_dict["operation_object"]
        log["execution_status"] = OrderStatus.doing
        current_app.logger.info(u'创建订单日志')
        log["order_id"] = self.order_id
        DisOrderLogService.created_order_log(log)
        target = 'TravelCloud'
        process_id = 'TCCommonProcess'
        transition_id = 'Link_0'
        sys_id = '0'
        domain = 'rootDomain'
        startnode_id = 'Start'
        announcer = 'hxyun'
        params = dict()
        # 任务id
        params['TaskID'] = self.com_async_task_id
        # 需求简述
        params['ReqbriefDesc'] = apply_info['ReqbriefDesc']
        # 请求者
        params['requestor'] = g.user['user_real_name']
        # 工作需求描述
        params['JobReqdesc'] = apply_info['JobReqdesc']
        current_app.logger.info(u'生成工单')
        result = RestClient.create_ticket(target, process_id, transition_id, sys_id, domain, startnode_id, announcer,
                                          params)
        return result

    def start_work(self):
        """ 重写start_work方法"""
        result = self.add_backup_ticket()
        result_id = eval(result)
        self.result = result_id
        if 'error' not in result_id.keys():
            DisOrder.update_order_ticket(self.order_id, result_id['id'])
            current_app.logger.info(u'添加异步任务')
            self.add_async_task(interval_time=300)
            return True
        else:
            current_app.logger.info(u'工单创建失败：%s' % result)
            DisOrderService.update_order_status(self.order_id, OrderStatus.failure)
            log = dict()
            log["operation_name"] = self.init_dict['operation_name']
            log["operation_object"] = self.init_dict["operation_object"]
            log["execution_status"] = OrderStatus.failure
            current_app.logger.info(u'创建订单日志')
            log["order_id"] = self.order_id
            DisOrderLogService.created_order_log(log)
            ComAsyncTask.del_com_task(self.com_async_task_id)
            return False

