
# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import g

from app.deployment.base.base import BaseAlloc



class gsWorker(object):
    """
    执行接口基类
    """
    def __init__(self,order_id,taskid,data):
        self.order_id = order_id
        self.task_id = taskid
        self.formated_parm = {'gs_info': data['Security_group_info']
                              }


    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
#         s = requests.session()
#         ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
#         status = ret.status_code

        f5_dict = g.request(url='http://127.0.0.1:5001/', method='post', data=helpers.json_dumps(self.formated_parm))
        
        if f5_dict['code'] == 200:
            back_ground_scheduler.add_job(self.__class__.__name__.get_work_status, 'interval', seconds=60, jobstore='test_sch',
                                          args=[self.order_id])

    @staticmethod
    def get_work_status(job_id):
        """
        查询执行状态（需要重载）
        :return:
        """
        from app.process.task import TaskService

        ret = g.request(url='',method='post', data=helpers.json_dumps(self.order_id))
        if ret['status_code'] == 200:
            back_ground_scheduler.remove_job(job_id=job_id,jobstore='')
            TaskService.update_task() #回调task