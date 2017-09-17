# !/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from app.utils import client
from flask import g
from app.utils import helpers
# from app.configs.api_uri import f5 as f5_
from app.deployment.base.base import BaseAlloc, BaseWorker
# from app.process.config import AllocRes
from app.configs.api_uri import network
from app.order.models import DisOrderLog
from app.utils.format import format_result
from flask import current_app

class GetF5(BaseAlloc):
    """
        wyj 2016-12
        GET F5
    """
     
    def __init__(self, data, order_id):
        apply_info = helpers.json_loads(data["apply_info"])
        self.formated_parm = {"order_id" :order_id,
                              "hypervisor_type": apply_info["hypervisor_type"],
                              "virtualserver":
                                  {
                                  "rip": apply_info["rip"],
                                  "rport": apply_info["rport"],
                                  "vip": data["vip"],
                                  "vport": apply_info["vport"]
                                  }
                              }


    def compute(self):

        getf5_info_uri = network.get_full_uri(network.GETF5_MARKED_URI)
        # if g.request:
        if hasattr(g, "request"):
            status, data, content = g.request(uri=getf5_info_uri, method="post", body=helpers.json_dumps(self.formated_parm))
        else:
            headers = {"content-type": "application/json"}
            f5_info = requests.post(url=getf5_info_uri, data=helpers.json_dumps(self.formated_parm), headers=headers)
        # print f5_info
        #         json_data = response.json
        return data
    
class F5BuildParm(object):
    """
      wyj 2016-12
            准备参数基类
    """
    def __init__(self,task_parm,data):
        self.devices = data["devices"]

    def format_parm(self):
        """

        :return:
        """
        devices_dict = {"devices":self.devices}
        return devices_dict
    
# class F5ReleaseRes(object):
#     """
#     释放资源基类
#     """
#     def __init__(self,order_id):
#         self.order_id = order_id
#         
#     def release_res(self):
#         release = g.request(url="", method="post", data=self.order_id)
# 
#         return release
        
class F5Worker(BaseWorker):
    """
    执行接口基类
    """
    def __init__(self,order_id,order_apply_info, item_id=None, com_async_task_id=None, nodename=None,data=None,task_info = None,task_timeout = None,
                                        item_no = None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        self.com_async_task_id = int(com_async_task_id)
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]["app_token"]
        self.app_token = token_
        data = helpers.json_loads(data)
        apply_info = helpers.json_loads(data["apply_info"])
        self.formated_parm = {"order_id": order_id,
                              "task_id": com_async_task_id,
                              "tenant_id": data["tenant_id"],
                              "hypervisor_type": apply_info["hypervisor_type"],
                              "data":[{
                                  "devices": data["devices"],
                                  "virtualserver":
                                      {
                                  "vip": data["vip"],
                                  "rip": apply_info["rip"],
                                  "rport": apply_info["rport"],
                                  "vport": apply_info["vport"],
                                  "ssl":apply_info["ssl"],
                                  "apptype":apply_info["apptype"],
                                  "idletimeout":apply_info["idletimeout"],
                                  "persistmethod": apply_info["persistmethod"],
                                  "description": apply_info["Remarks"]
                                        }
                                  }
                                  ]
                              }
        self.task_info = task_info
        self.kls = self.__class__
        self.order_apply_info = order_apply_info
        self.node_name = nodename
        self.timeout = task_timeout
        self.data = data
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
            operation_name=u"create_f5_lbpolicy",
            operation_object=self.data["vip"],
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)
        current_app.logger.info(u"formated_parm====".format(self.formated_parm))

        f5work_info_uri = network.get_full_uri(network.F5WORK_MARKED_URI)
        current_app.logger.info(u"负载均衡传参：".format(helpers.json_dumps(self.formated_parm)))
        # if hasattr(g, "request"):
            # status, data, content = g.request(uri=f5work_info_uri, method="post", body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=f5work_info_uri,
                                                    body=self.formated_parm, method="post",
                                                    app_token=self.app_token)

        current_app.logger.info(u"data111====".format(data))
        current_app.logger.info(u"status111====".format(status))
        self.init_dict["operation_object"] = self.data["vip"]
        self.init_dict["operation_name"] = "create_f5_lbpolicy"
        if status:
            self.add_async_task()
            return True, "start work"
        else:
            return None

class F5Delete(BaseWorker):

    def __init__(self,order_id,order_apply_info, item_id=None, com_async_task_id=None, nodename=None,data=None,task_info = None,task_timeout = None,
                                        item_no = None):
        from app.order.models import DisOrder
        self.order_id = order_id
        self.item_id = str(item_id)
        token_info = DisOrder.get_order_details(order_id)
        token_ = format_result(token_info)[0]["app_token"]
        self.app_token = token_
        self.com_async_task_id = int(com_async_task_id)
        apply_info = helpers.json_loads(order_apply_info)
        self.formated_parm = {"order_id": self.order_id,
                              "task_id": self.com_async_task_id,
                              "data":
                                  {
                                      "name":apply_info["f5_name"]
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
            operation_name=u"delete_f5_lbpolicy",
            operation_object=self.formated_parm["data"]["name"],
            execution_status=u"doing",
            order_id=self.order_id
        )
        DisOrderLog.created_order_log(log)

        current_app.logger.info(u"formated_parm====".format(self.formated_parm))
        f5delete_info_uri = network.get_full_uri(network.F5DELETE_MARKED_URI)
        # if hasattr(g, "request"):
        # status, data, content = g.request(uri=f5delete_info_uri, method="post", body=helpers.json_dumps(self.formated_parm))
        status, data, content = client.task_request(uri=f5delete_info_uri,
                                                    body=helpers.json_dumps(self.formated_parm), method="post",
                                                    app_token=self.app_token)
        self.init_dict["operation_object"] = self.formated_parm["data"]["name"]
        self.init_dict["operation_name"] = "delete_f5_lbpolicy"
        current_app.logger.info(u"status====".format(status))
        current_app.logger.info(u"data====".format(data))
        if status:
            self.add_async_task()
            return True, "start delete"
        else:
            return None
