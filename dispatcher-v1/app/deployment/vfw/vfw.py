# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from flask import g

from app.utils import helpers
# from app.configs.api_uri import vfw as vfw_
from app.deployment.base.base import BaseAlloc, BaseWorker
from app.deployment.vfw.models import AsyncTask
from app.configs.api_uri import network
from app.utils import client
from app.utils.format import format_result
from app.order.models import DisOrderLog
from flask import current_app


class VfwWorker(BaseWorker):
    """
    执行接口基类
    """
    def __init__(self,order_id,order_apply_info, item_id=None, com_async_task_id=None, nodename=None,data=None,task_info = None,task_timeout = None,
                                        item_no = None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        data = helpers.json_loads(data)
        apply_info = helpers.json_loads(data['apply_info'])
        # result = AsyncTask.get_async_task_result(order_id, com_async_task_id)
        # service = [apply_info['protocol'] + '_' + i for i in apply_info['port']]
        service = []

        for p in apply_info['protocol']:
            service1 = [p + '_' + i for i in apply_info['port']]
            service = service + service1

        # result = helpers.json_loads(result)
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        self.formated_parm = {'order_id': order_id,
                              'task_id': com_async_task_id,
                              'tenant_id': data['tenant_id'],
                              'data': [{
                                  'policy': {
                                      'src': apply_info['src'],
                                      'dst': apply_info['dst'],
                                      'service': service,
                                      'action': apply_info['action'],
                                      'direction': apply_info['direction']
                                        },
                                  'devices': data['devices']['v_fw'],

                                  }
                                  ]
                              }
        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.init_dict = {}

    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
        # s = requests.session()
        # ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        # status = ret.status_code

        src_list = ','.join(self.formated_parm['data'][0]['policy']['src'])
        dst_list = ','.join(self.formated_parm['data'][0]['policy']['dst'])
        ip_list = src_list + ',' + dst_list
        log = dict(
            operation_name=u"create_firewall",
            operation_object=ip_list,
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)

        current_app.logger.info(u"formated_parm====".format(self.formated_parm))
        vfwwork_info_uri = network.get_full_uri(network.VFWWORK_MARKED_URI)
        # if hasattr(g, "request"):
            # status, data, content = g.request(uri=vfwwork_info_uri, method='post', body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=vfwwork_info_uri,
                                                    body=helpers.json_dumps(self.formated_parm), method='post',
                                                    app_token=self.app_token)

        current_app.logger.info(u"data111====".format(data))
        current_app.logger.info(u"status111====".format(status))
        self.init_dict['operation_object'] = ip_list
        self.init_dict['operation_name'] = 'create_firewall'
        if status:
            self.add_async_task()
            return True, 'start work'
        else:
            return None


class VFwDelete(BaseWorker):
    def __init__(self, order_id, order_apply_info, item_id=None, com_async_task_id=None, nodename=None, data=None,
                 task_info=None, task_timeout=None,item_no=None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]['app_token']
        self.app_token = token_
        apply_info = helpers.json_loads(order_apply_info)
        self.formated_parm = {'order_id': self.order_id,
                              'task_id': self.com_async_task_id,
                              'data':
                                  {
                                      'name': apply_info['vfw_name'],
                                      'id': apply_info['virtual_fw_policy_id']
                                  }
                              }

        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.init_dict = {}

    def start_work(self):
        """
        根据订单号和节点名称调执行接口,并建立定时轮询任务（查询执行状态）
        :param order_id:
        :param node_name:
        :return:
        """
        # s = requests.session()
        # ret = s.post(url=ApiMapping().work_dic[self.node_name],data=None)
        # status = ret.status_code
        log = dict(
            operation_name=u"delete_firewall",
            operation_object=self.formated_parm['data']['name'],
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)

        vfwdelete_info_uri = network.get_full_uri(network.VFWDELETE_MARKED_URI)
        # if hasattr(g, "request"):
        #     status, data, content = g.request(uri=vfwdelete_info_uri, method='post', body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=vfwdelete_info_uri,
                                                    body=helpers.json_dumps(self.formated_parm), method='post',
                                                    app_token=self.app_token)

        current_app.logger.info(u"data111====".format(data))
        current_app.logger.info(u"status111====".format(status))
        self.init_dict['operation_object'] = self.formated_parm['data']['name']
        self.init_dict['operation_name'] = 'delete_firewall'
        if status:

            self.add_async_task()
            return True, 'start delete'
        else:
            return None