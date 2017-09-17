#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    dgl 2016-11-10
    worker
"""
from app.deployment.constant import ApiMapping
import requests

class Worker(object):
    """
    调用执行接口
    """
    def __init__(self,order_id,node_name):
        """
        :param order_id: 订单号
        :param node_name: 节点名称
        """
        self.order_id = order_id
        self.node_name = node_name

    def start_work(self):
        """
        根据订单号和节点名称调执行接口
        :param order_id:
        :param node_name:
        :return:
        """
        s = requests.session()
        ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        status = ret.content
        return status

    def get_work_status(self):
        """
        根据订单号和节点名称查询执行状态
        :param order_id:
        :param nodename:
        :return:
        """
        pass

    def release_resource(self,order_id):
        """
        释放资源接口
        :param order_id:
        :return:
        """
        pass


class Computer(object):
    """
    计算接口
    """
    def __init__(self,order_data):
        """

        :param order_data:
        """
        self.order_data = order_data

    def compute(self):
        """
        根据订单信息调用计算接口
        :return: 计算结果
        """
        pass

class TimingTask(object):
    """
    循环定时查询任务
    """
    def __init__(self):
        pass

    def poll_status(self,func):
        """
        轮询订单执行状态
        :param func:
        :return:
        """
        pass

