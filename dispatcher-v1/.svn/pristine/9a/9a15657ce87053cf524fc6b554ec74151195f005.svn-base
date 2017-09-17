# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -11-23
"""
import httplib
import json
import re

import time

from flask import current_app
from six.moves import http_client
from app.configs.api_uri import titsm


class RestClient():
    @classmethod
    def get_url_data(cls, method, url, param=None, headers=None):
        """
        使用httplib的方式获取指定url的响应数据
        :param method: http请求的方法（POST，GET，PUT，DELETE等）
        :param url: url访问体
        :param param: 请求参数（字典形式）
        :param headers: 请求头（字典形式）
        :return:
        """
        headers = {} if not headers else headers
        param = {} if not param else param

        try:
            ipr = re.search("\d+\.\d+\.\d+\.\d+", url)
            portr = re.search("(:)(\d+)",url)
            ip = ipr.group()
            port = portr.group(2)
            conn = http_client.HTTPConnection(ip,port)
            conn.request(method, url, json.dumps(param), headers)
            response = conn.getresponse()
            data = response.read()
            # print response.status
            if response.status == 200:
                print 'Access successful！'
                print 'result'+data
                return data
            else:
                print response.status
                print 'Access failed！'
                return 'Access_failed'
        except Exception, e:
            print e
        finally:
            conn.close()

    @classmethod
    def get_result(cls, methd, paras):
        params = dict()
        params['userid'] = titsm.USER_ID
        params['password'] = titsm.PASSWORD
        params['linkurl'] = titsm.LINKURL
        params['value'] = paras
        params['method'] = methd
        url = titsm.URL
        header = titsm.HEADER
        method = 'POST'
        result = RestClient.get_url_data(method, url, param=params, headers=header)
        current_app.logger.debug("TITSM---------------")
        current_app.logger.debug("调用方法---------------" + methd)
        current_app.logger.debug("返回结果---------------" + result)

        return result

    @classmethod
    def query_by_id_instances(cls, id_):
        #获取指定配置项信息
        param = dict()
        param['id'] = id_
        method = titsm.QUERY_BY_ID_INSTANCES
        return cls.get_result(method,param)

    @classmethod
    def query_info_instances(cls, tplcode, filter_):
        #查询配置项信息
        param = dict()
        param['tplCode'] = tplcode
        param['filter'] = filter_
        method = titsm.QUERY_INFO_INSTANCES
        return cls.get_result(method,param)

    @classmethod
    def query_relationships_by_id_instances(cls, id_):
        # 获取指定配置项的关系
        param = dict()
        param['id'] = id_
        method = titsm.QUERY_RELATIONSHIPS_BY_ID_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def delete_instances(cls, id_):
        # 删除配置项
        param = dict()
        param['id'] = id_
        method = titsm.DELETE_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def save_instances(cls, template_code, values, src_sys, src_id):
        # 添加配置项
        '''
        :param template_code:
        :param instance:配置项各项值（dict）
        :param src_sys:
        :param src_id:
        :param update_time:
        :return:
        '''

        param = dict()
        instance_source = dict()
        instance = dict()
        instance['templateCode'] = template_code
        instance['values'] = values
        instance['resourceChangePersonId'] = titsm.RESOURCE_CHANGE_PERSON_ID
        instance_source['srcSys'] = src_sys
        instance_source['srcId'] = src_id
        instance_source['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        param['instance'] = instance
        param['instanceSource'] = instance_source
        method = titsm.SAVE_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def update_instances(cls, id_,template_code, values, src_sys, src_id):
        # 修改配置项
        param = dict()
        instance = dict()
        instance_source = dict()
        instance['id'] = id_
        instance['templateCode'] = template_code
        instance['values'] = values
        instance['resourceChangePersonId'] = titsm.RESOURCE_CHANGE_PERSON_ID
        instance_source['srcSys'] = src_sys
        instance_source['srcId'] = src_id
        instance_source['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        param['instance'] = instance
        param['instanceSource'] = instance_source
        method = titsm.SAVE_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def save_relationships_instances(cls, src, dest, template_code, name, src_sys, src_id):
        # 添加单个关系
        param = dict()
        relationship = dict()
        instance_source = dict()
        relationship['src'] = src
        relationship['dest'] = dest
        relationship['templateCode'] = template_code
        relationship['name'] = name
        instance_source['srcSys'] = src_sys
        instance_source['srcId'] = src_id
        instance_source['updateTime'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        param['relationship'] = relationship
        param['instanceSource'] = instance_source
        method = titsm.SAVE_RELATIONSHIPS_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def delete_relationships_instances(cls, id_):
        # 删除关系
        param = dict()
        param['id'] = id_
        method = titsm.DELETE_RELATIONSHIPS_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    def audit_change_instances(cls, type, tempalte_code, id_):
        # 审核/放弃 配置项变更
        param = dict()
        param['type'] = type
        param['tempalteCode'] = tempalte_code
        param['id'] = id_
        method = titsm.AUDIT_CHANGE_INSTANCES
        return cls.get_result(method, param)

    @classmethod
    # def create_ticket(cls, param):
    def create_ticket(cls, target, process_id, transition_id, sys_id, domain, startnode_id, announcer, param):
        # 创建工单
        # target:业务模块标识（必须），应该是业务模块id
        # processId:流程id
        # transitionId:迁移路径id
        # sysId:外部系统标识
        # domain:域标识
        # startNodeId:启动节点id
        # Announcer：用户名
        # param 创建工单要传入的属性
        param['target'] = target
        param['processId'] = process_id
        param['transitionId'] = transition_id
        param['sysId'] = sys_id
        param['domain'] = domain
        param['startNodeId'] = startnode_id
        param['announcer'] = announcer
        method = titsm.CREATE_TICKET
        return cls.get_result(method, param)

    @classmethod
    def deleteticket(cls, ticketid):
        # 删除工单
        # ticketid:工单ID
        param = dict()
        param['ticketid'] = ticketid
        method = titsm.DELETE_TICKET
        return cls.get_result(method, param)

    @classmethod
    def query_ticket_relations(cls, relateid, relatetype):
        # 查询工单关联信息
        # relateId: 工单id
        # relateType: 关联字段类型[relatedTicket、relateResource、relateAsset]
        param = dict()
        param['relateId'] = relateid
        param['relateType'] = relatetype
        method = titsm.QUERY_TICKET_RELATIONS
        return cls.get_result(method, param)

    @classmethod
    def query_ticket(cls, id_):
        # 根据工单id查询工单
        # id: 工单ID
        param = dict()
        param['id'] = id_
        method = titsm.QUERY_TICKET
        return cls.get_result(method, param)

    @classmethod
    def add_ticket_relations(cls, relateid, childrenrelateid, memo, relatecode):
        # 添加工单与工单的关联关系
        # relateId： 工单ID
        # childrenRelateId ： 被关联工单ID
        # memo ： 备注
        # relateCode:    关联编码（模块id_2_模块id）
        # relateType:    relatedTicket
        param = dict()
        param['relateId'] = relateid
        param['childrenRelateId'] = childrenrelateid
        param['memo'] = memo
        param['relateCode'] = relatecode
        param['relateType'] = 'relatedTicket'
        method = titsm.ADD_TICKET_RELATIONS
        return cls.get_result(method, param)

    @classmethod
    def add_ticket_relations_resources(cls, relateid, childrenrelateid, memo, relatecode):
        # 添加工单与资源的关联关系
        # relateId ： 工单ID
        # childrenRelateId ： 被关联配置项ID
        # memo ： 工单关联配置项
        # relateCode:    关联编码
        # relateType:    relateResource
        # bizCode:     relateResource
        param = dict()
        param['relateId'] = relateid
        param['childrenRelateId'] = childrenrelateid
        param['memo'] = memo
        param['relateCode'] = relatecode
        param['relateType'] = 'relateResource'
        param['bizCode'] = 'relateResource'
        method = titsm.ADD_TICKET_RELATIONS_RESOURCES
        return cls.get_result(method, param)

    @classmethod
    def del_ticket_relations(cls, relateid, childrenrelateid, relatetype):
        # 删除关联关系
        # relateId ： 工单ID
        # childrenRelateId    ：被关联工单id
        # relateType： 关联关系类型（关联的是资源relateResource / 工单relatedTicket）
        param = dict()
        param['relateId'] = relateid
        param['childrenRelateId'] = childrenrelateid
        param['relateType'] = relatetype
        method = titsm.DEL_TICKET_RELATIONS
        return cls.get_result(method, param)

    @classmethod
    def update_ticket(cls, ticketid, transition, resolverid, memo):
        # 工单流程扭转
        # ticketId ： 工单ID（必传）
        # transition ： 流程处理线（必传)
        # resolverId：处理人帐号（必传）
        # memo ： 备注 “工单流转”
        param = dict()
        param['ticketId'] = ticketid
        param['transition'] = transition
        param['resolverId'] = resolverid
        param['memo'] = memo
        method = titsm.UPDATE_TICKET
        return cls.get_result(method, param)

    @classmethod
    def update_ticket_properties(cls,param):
        # 工单流程扭转
        # ticketId ： 工单ID（必传）
        # code ： value(工单属性Code)
        if 'ticketId' not in param.keys():
            return u'缺少ticketId'
        method = titsm.UPDATE_TICKET_PROPERTIES
        return cls.get_result(method, param)

    @classmethod
    def query_ticket_by_resourceid(cls, id_):
        # 工单流程扭转
        # id: 配置项ID
        param = dict()
        param['id'] = id_
        method = titsm.QUERY_TICKET_BY_RESOURCEID
        return cls.get_result(method, param)

    @classmethod
    def query_tickets(cls, param):
        # 工单流程扭转
        # moduleid 模块ID（必传）
        # respurpose 业务对象属性
        if 'moduleId' not in param.keys():
            return u'缺少moduleId'
        method = titsm.QUERY_TICKETS
        return cls.get_result(method, param)

    @classmethod
    def assig_nwork(cls, ticketid, actors, assignuser, taskid):
        # 改派接口
        # ticketId: 工单号
        # actors: 修改后的执行人
        # assignUser: 操作人
        # taskId:任务id
        param = dict()
        param['ticketId'] = ticketid
        param['actors'] = actors
        param['assignUser'] = assignuser
        param['taskId'] = taskid
        method = titsm.ASSIG_NWORK
        return cls.get_result(method, param)

    @classmethod
    def query_unclosed_tickets(cls, moduleid, processid):
        # 查询未结束的工单
        # moduleId: 模块id
        # processId: 流程id
        param = dict()
        param['moduleId'] = moduleid
        param['processId'] = processid
        method = titsm.QUERY_UNCLOSED_TICKETS
        return cls.get_result(method, param)


if __name__ == '__main__':
    ticketid = '9e701abe-eb47-4155-9c08-7d7ad6d7a42e'
    RestClient = RestClient()
    resource = RestClient.query_info_instances('IntranetIPSubnet', 'IPSubnet:=:10.6.106.0')
    # resource = RestClient.query_ticket(ticketid)
    # resource = RestClient.query_ticket_relations(ticketid, 'relateResource')
    data = eval(resource)
    # insdic = dict()
    # insdic['CiName'] = 'IP-10.66.157.91'
    # result =  RestClient.update_instances('ae2c2ce6-1ee4-4cb9-bfad-fc7c15873d07','IntranetIPAddr', insdic, 'radar', 'radar')
    # print  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    # RestClient.get_url_data( 'GET', 'http://127.0.0.1:5000/api/testyg/index?sex=男&&id=1',
    #              headers={'Content-Type': 'application/json;charset=utf-8'})
