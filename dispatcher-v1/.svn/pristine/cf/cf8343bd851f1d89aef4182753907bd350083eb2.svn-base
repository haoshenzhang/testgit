# !/usr/bin/python
# -*- coding: utf-8 -*-

#disable

from app.deployment.base.base import BaseAlloc,BaseBuildParm,BaseWorker
import requests
from app.process.models import ProcessMappingTaskItem,ProcessMappingTask
from app.configs.api_uri import operation as op
from app.utils import helpers

class BigEyeParameterBuildParm(BaseBuildParm):
    """
    daiguanlin@126.com
    bigeye处理返回data的类
    """
    def __init__(self,data,result):
        self.data = data
        self.result = result

    def format_parm(self):
        return self.result

class BigEyeParameterWorker(BaseWorker):
    """
    daiguanlin@126.com
    bigeye调参数worker类
    """
    def start_work(self):
        work_list = ProcessMappingTaskItem.get_task_item_list_by_node_name(self.order_id,'create_vm')
        target_item_info = work_list[self.item_no]
        ip_ = target_item_info.get('ip', None)
        if not ip_:
            ip_ = target_item_info.get('fixed_ip')
        self.target_item_ip = ip_
        bigeye_alloc_data = ProcessMappingTask.get_task_info(self.order_id)
        self.bigeye_ip = bigeye_alloc_data['Bigeye_alloc_info']['bigeye_ip']
        self.formated_parm = helpers.json_dumps(self.format_para())
        bigeye_parameter_create_uri = op.get_full_uri(op.CREATE_BIGEYE_PARAMETER_URI)
        res = requests.post(url=bigeye_parameter_create_uri, data=self.formated_parm, headers=op.HEADERS).json()
        if res['status'] == u'10000':
            self.add_async_task(interval_time=20)
            return True, 'start work'
        else:
            return None

    def pre(self):
        pass

    def format_para(self):
        return dict(
            destip = self.target_item_ip,
            hostname = '',
            name = ''
        )