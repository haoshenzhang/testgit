# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    dgl 2016-07-28
"""
import logging

from app.deployment.constant import ApiMapping
import requests
from app.extensions import back_ground_scheduler,db
from app.deployment.models import ComAsyncTask
from app.process.models import ProcessMappingTaskItem
from app.utils import helpers
import time,datetime
from flask import current_app

from app.utils.format import format_result


def get_class(class_name):
    try:
        return globals()[class_name]
    except AttributeError:
        raise Exception('%s is not defined!' % class_name)

class BaseBuildParm(object):
    """
    准备参数基类
    """
    def __init__(self,parm):
        self.parm = parm

    def json2dict(self):
        self.parm = dict(helpers.json_loads(self.parm))
        return self.parm

    def format_parm(self):
        """

        :return:
        """

        return


class BaseAlloc(object):
    """
    计算分配资源基类
    """
    def __init__(self,order_id,nodename,formated_parm=None):
        self.order_id = order_id
        self.node_name = nodename
        self.formated_parm = formated_parm

    def compute(self):
        """

        :return:
        """
        response = requests.post(url='',data=self.formated_parm)
        res_json = response.json()
        return res_json


class BaseReleaseRes(object):
    """
    释放资源基类
    """
    def __init__(self):
        pass


class BaseWorker(object):
    """
    执行接口基类
    """
    def __init__(self, order_id, order_apply_info, item_id=None, com_aysnc_task_id=None, nodename=None, data=None,
                 task_info=None, timeout=None, item_no=None):
        """

        :param order_id: 订单id
        :param order_apply_info:  订单中的apply_info字段
        :param item_id:  dis_process_task_item 中的id
        :param com_aysnc_task_id: com_async_taak 表中的id
        :param nodename: 流程中的节点名称
        :param data:  请求接口的data
        :param item_no:  task_list 中的序号
        """
        self.order_id = int(order_id)
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.data = data
        self.com_async_task_id = int(com_aysnc_task_id)
        self.item_id = str(item_id)
        self.task_info = task_info
        self.kls = self.__class__
        self.timeout = timeout
        self.item_no = item_no
        from app.order.models import DisOrder
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        self.init_dict = dict(
            order_apply_info=self.order_apply_info,
            nodename=self.node_name,
            data=self.data,
            com_aysnc_task_id=self.com_async_task_id,
            item_id=self.item_id,
            task_info=self.task_info,
            item_no=self.item_no
        )

    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
        s = requests.session()
        ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        status = ret.status_code

        if status == 503:
            self.add_async_task()
            return True,'start work'
        else:
            return None

    def add_async_task(self,interval_time=30):
        """
        添加异步任务,timeout = 0 代表没有超时时间
        :return:
        """
        current_app.logger.info(u"异步排查 准备建立异步任务,插入apscheduler表")
        if self.timeout:
            expire_time = time.time() + int(self.timeout)
        if self.timeout == None or self.timeout == 0:
            expire_time = None
        current_app.logger.info(u"异步排查 id={}".format(self.item_id))
        current_app.logger.info(u"异步排查 seconds={}".format(interval_time))
        current_app.logger.info(u"异步排查 args={}".format([self.item_id, self.com_async_task_id, self.order_id, self.task_info,self.kls,
                                            expire_time, self.init_dict]))
        back_ground_scheduler.add_job(id=self.item_id, func=get_work_status, trigger='interval', seconds=interval_time,
                misfire_grace_time=3600*12, max_instances=20, args=[self.item_id, self.com_async_task_id, self.order_id, self.task_info,self.kls,
                                            expire_time, self.init_dict])
        current_app.logger.info(u"异步排查 插入任务表成功")

    @staticmethod
    def finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict, com_async_task_id):
        """
        结束轮询最后调用此方法
        :param order_id: 订单id
        :param task_info: dis_process_task_item 中每条item数据
        :param com_async_task_status:  com_async_task 中的status
        :param com_async_task_result: com_async_task 中的result
        :return:
        """
        from app.process.task import TaskService
        operation_object = init_dict.get('operation_object',None)
        operation_name = init_dict.get('operation_name',None)
        plug = init_dict.get('plug', None)
        TaskService.update_task(order_id, task_info, com_async_task_status, com_async_task_result, com_async_task_id,
                                operation_object=operation_object, operation_name=operation_name, plug=plug)

    @staticmethod
    def update_cmdb(cmdb_data):
        """
        更新CMDB
        :param cmdb_data:
        :return:
        """
        pass


def get_work_status(job_id, com_async_task_id, order_id, task_info, kls, expire_time, init_dict):
    """
    :param job_id:
    :param com_async_task_id:
    :param order_id:
    :param task_info:
    :param kls:
    :return:
    """
    with back_ground_scheduler.app.app_context():
        # wfluo add db session flush操作
        # ComAsyncTask.app_context_flush()

        current_app.logger.info(u"轮询com_async_task中 Base,order_id:{},com_async_task_id:{}".format(order_id,com_async_task_id))
        com_async_task_info = ComAsyncTask.get_async_task_status(order_id, com_async_task_id)
        task_info.update({'async_task_id': com_async_task_id})
        com_async_task_status = com_async_task_info['status']
        current_app.logger.info(u"com_async_task status:{}".format(com_async_task_status))
        if com_async_task_info['code'] == 1:
            current_app.logger.info(u"异步任务已完成")
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            # 结束异步任务,调用节点的finish
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result, init_dict, com_async_task_id)

        if com_async_task_info['code'] != None and com_async_task_info['code'] != 1:
            current_app.logger.info(u"异步任务失败Base，order_id:{},com_async_task_id:{}".format(order_id,com_async_task_id))
            com_async_task_result = com_async_task_info['result']
            back_ground_scheduler.delete_job(id=job_id)
            com_async_task_status = u"failed"
            kls.finish_work(order_id, task_info, com_async_task_status, com_async_task_result,init_dict,com_async_task_id)  # 结束异步任务,调用节点的finish

        if expire_time != None:
            now_ = time.time()
            if now_ > expire_time:
                # 将任务改为timeout并删除异步任务
                current_app.logger.info(u"异步任务超时")
                current_app.logger.info(u"当前时间:{}".format(now_))
                current_app.logger.info(u"过期时间:{}".format(expire_time))
                ProcessMappingTaskItem.update_status('timeout',order_id,job_id,'running')
                back_ground_scheduler.delete_job(id=job_id)

