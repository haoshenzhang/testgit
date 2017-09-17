# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    订单服务层
"""
from string import lower

from flask import current_app
from flask import g
from flask import json

from app.extensions import db
from app.order.constant import OrderStatus, NodeStatus, Translation
from app.order.models import DisOrder, DisOrderLog
from app.utils.format import format_result


class DisOrderService(object):
    """
    wei lai 2016/12/14
    DisOrderService层(订单service)
    """

    @staticmethod
    def get_order_list(args):
        """
         wei lai 2016/12/14
         功能：我的订单 （根据用户ID查询订单列表）
        :param user_id:
        :return:订单列表
        """
        page = args['page']
        per_page = args['per_page']
        start = (page - 1) * per_page
        args['start'] = start
        args['per_page'] = per_page
        # 如果是超级管理员，也只是查询自己的订单
        if hasattr(g, "user") and g.user.get("system_admin") == u'1':
            args['user_id'] = g.user['current_user_id']
        # 如果时候租户管理员，查询该租户下的所有订单
        if hasattr(g, "tenant") and g.tenant.get("is_admin"):
            args['tenant_id'] = g.tenant.get("tenant_id")
        if g.user.get("system_admin") == u'0' and not g.tenant.get("is_admin"):
            args['user_id'] = g.user['current_user_id']
            args['tenant_id'] = g.tenant.get("tenant_id")
        if 'serial_number' in args['keyword'] and args['keyword']['serial_number']:
            args['keyword']['serial_number'] = u''.join(['%', args['keyword']['serial_number'], '%'])
            args['serial_number'] = args['keyword']['serial_number']
        if 'resource_type' in args['keyword'] and args['keyword']['resource_type']:
            args['resource_type'] = args['keyword']['resource_type']
        if 'status' in args['keyword'] and args['keyword']['status']:
            args['status'] = args['keyword']['status']
        if 'application_name' in args['keyword'] and args['keyword']['application_name']:
            args['keyword']['application_name'] = u''.join(['%', args['keyword']['application_name'], '%'])
            args['application_name'] = args['keyword']['application_name']
        if 'starttime' in args['keyword'] and args['keyword']['starttime']:
            args['starttime'] = args['keyword']['starttime']
        if 'endtime' in args['keyword'] and args['keyword']['endtime']:
            args['endtime'] = args['keyword']['endtime']
        order_list = DisOrder.get_order_list_by_args(args)
        order_list = format_result(order_list)
        translation = Translation.resource_type_chinese()
        if order_list:
            for i in order_list:
                # if i['apply_info'] != u"{}":
                    # apply_info = i['apply_info']
                    # i['apply_info'] = json.loads(apply_info)
                resource_type = i['resource_type']
                i.pop('app_token')
                if resource_type in translation:
                    resource_type = translation[resource_type]
                else:
                    resource_type = resource_type + u"（不规范资源类型）"
                i['resource_type'] = resource_type
        return order_list

    @staticmethod
    def get_count_by_condition(args):
        """
        查询资源池条数
        :param args:参数值
        :return:
        """
        # 如果是超级管理员，查询所有的订单
        if hasattr(g, "user") and g.user.get("system_admin") == u'1':
            args['user_id'] = g.user['current_user_id']
        # 如果时候租户管理员，查询该租户下的所有订单
        if hasattr(g, "tenant") and g.tenant.get("is_admin"):
            args['tenant_id'] = g.tenant.get("tenant_id")
        if g.user.get("system_admin") == u'0' and not g.tenant.get("is_admin"):
            args['user_id'] = g.user['current_user_id']
        if 'serial_number' in args['keyword'] and args['keyword']['serial_number']:
            args['keyword']['serial_number'] = u''.join(['%', args['keyword']['serial_number'], '%'])
            args['serial_number'] = args['keyword']['serial_number']
        if 'resource_type' in args['keyword'] and args['keyword']['resource_type']:
            args['resource_type'] = args['keyword']['resource_type']
        if 'status' in args['keyword'] and args['keyword']['status']:
            args['status'] = args['keyword']['status']
        if 'application_name' in args['keyword'] and args['keyword']['application_name']:
            args['keyword']['application_name'] = u''.join(['%', args['keyword']['application_name'], '%'])
            args['application_name'] = args['keyword']['application_name']
        if 'starttime' in args['keyword'] and args['keyword']['starttime']:
            args['starttime'] = args['keyword']['starttime']
        if 'endtime' in args['keyword'] and args['keyword']['endtime']:
            args['endtime'] = args['keyword']['endtime']
        total_count = DisOrder.get_order_condition_count(args)
        return total_count

    @staticmethod
    def get_order_details(order_id, field=None):
        """
        wei lai 2016/12/16
        功能：订单详情 （根据order_id）内部调用
        :param order_id:
        :return:订单详细信息
        """
        data = DisOrder.get_order_details(order_id)
        list_ = format_result(data)
        if list_:
            if field != None:
                return list_[0][field]
            else:
                return list_[0]
        else:
            return None

    @staticmethod
    def get_order_by_id(order_id):
        """
        wei lai 2017/2/16
        功能：订单详情 （根据order_id）外部接口
        :param order_id:
        :return:订单详细信息
        """
        data = DisOrder.get_order_details(order_id)
        list_ = format_result(data)
        translation = Translation.resource_type_chinese()
        if list_:
            if list_[0]['apply_info'] != u"{}":
                    apply_info = list_[0]['apply_info']
                    list_[0]['apply_info'] = json.loads(apply_info)
            resource_type = list_[0]['resource_type']
            list_[0].pop('app_token')
            if resource_type in translation:
                resource_type = translation[resource_type]
            else:
                resource_type = resource_type + u"（不规范资源类型）"
            list_[0]['resource_type'] = resource_type
        return list_[0]

    @staticmethod
    def create_order(args, commit=True):
        """
         wei lai 2016/12/14
         功能：创建订单
        :param args:dict{user_id: 用户ID ,tenant_id:租户ID, application_id:业务ID,resource_type:资源类型（虚机，物理机，IP）
                        operation_type:操作类型名称（创建虚机，创建VPN）,apply_info:订单申请信息}
        :param commit:默认为真
        :return:id_：订单ID
        """
        try:
            order_id, serial_number = DisOrder.created_order(args)
            commit and db.session.commit()
            return order_id, serial_number
        except Exception, e:
            current_app.logger.error(u'订单请求异常:{}，参数{}'.format(e, args), exc_info=True)
            raise Exception(e)
            return False

    @staticmethod
    def update_apply_info(order_id, apply_info, commit=True):
        """
         wei lai 2016/12/21
         功能：修改订单apply_info
        :param order_id: 订单ID
        :param apply_info:订单信息
        :param commit:默认为真
        """
        try:
            DisOrder.update_apply_info(order_id, apply_info)
            commit and db.session.commit()
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            ss = u"更改失败，检查参数是否正确"
            return ss

    @staticmethod
    def update_order_status(order_id, status, ticket_id=None, commit=True):
        """
         wei lai 2016/12/14
         功能：修改订单状态
        :param order_id: 订单ID
        :param commit:默认为真
        :param status:状态（done：订单完成；failure：订单失败）
        :param ticket_id: 工单ID
        """
        try:
            if ticket_id:
                DisOrder.update_order_status(order_id, status, ticket_id)
            else:
                DisOrder.update_only_status(order_id, status)
            commit and db.session.commit()
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            ss = u"更改失败，检查参数是否正确"
            raise Exception(e)
            return ss


class DisOrderLogService(object):
    """
    wei lai 2016/12/14
    DisOrderLogService层(订单service)
    """
    @staticmethod
    def get_order_log(order_id):
        """
         wei lai 2016/12/14
         功能：订单跟踪
        :param order_id:订单ID
        :return:订单跟踪信息
       """
        data = DisOrderLog.get_order_log(order_id)
        list_ = format_result(data)
        translation = Translation.operation_name_chinese()
        if list_:
            for i in list_:
                operation_name = i['operation_name']
                operation_object = i['operation_object']
                if u"失败" in operation_object:
                    i['operation_object'] = operation_object[0:-8]
                else:
                    i['operation_object'] = operation_object
                if operation_name in translation:
                    operation_name = translation[operation_name]
                else:
                    operation_name = operation_name + u"(不规范操作名称)"
                i['operation_name'] = operation_name
        return list_

    @staticmethod
    def created_order_log(args, commit=True):
        # type: (object, object) -> object
        """
         wei lai 2016/12/14
         功能：创建订单日志
        :param args:dict{order_id:订单ID,operation_object:操作对象（机器IP地址等）,operation_name:操作名称（具体的小步骤名称，如创建虚机分为10步，每个小步骤名称）
                        execution_status:执行状态（各个小步骤的执行状态，doing，done，failure. ）}
        :param commit:默认为真
        :return:
       """
        try:
            execution_status = args['execution_status']
            if execution_status == OrderStatus.doing:
                DisOrderLog.created_order_log(args)
            if execution_status == OrderStatus.succeed:
                DisOrderLog.finished_order_log(args)
            if execution_status == OrderStatus.failure:
                DisOrderLog.finished_order_log(args)
                DisOrderLog.update_operation_name(args)
            commit and db.session.commit()
            return True
        except Exception, e:
            current_app.logger.error(u'订单日志请求异常:{}'.format(e), exc_info=True)
            raise Exception(e)
            return False

    @staticmethod
    def repeat_order(order_id):
        """
        重做订单，只有失败订单可以从新做
        :param order_id:
        :return:
        """
        from app.process.task import TaskService
        # 根据订单id检测是否失败
        from app.process.models import ProcessMappingTaskItem
        task_info = ProcessMappingTaskItem.get_task_item_list(order_id)
        task_info = format_result(task_info)
        if task_info:
            for i in task_info:
                node_status = i['status']
                # 如果超时，失败执行重做
                if lower(node_status) == NodeStatus.failed or lower(node_status) == NodeStatus.timeout:
                    # 修改订单状态
                    status = OrderStatus.doing
                    DisOrder.update_status(order_id, status)
                    TaskService.start_task(order_id, 0)
                    ss = u"执行重做"
                    return ss
            else:
                ss = u"订单已完成或正在执行中,不可重做"
                return ss
        else:
            # 查询订单
            order = DisOrder.get_order_details(order_id)
            order = format_result(order)
            if order:
                status = OrderStatus.doing
                DisOrder.update_status(order_id, status)
                result1 = TaskService.create_task(order_id)
                if result1[0] and result1[1] == '成功':
                    TaskService.start_task(order_id, 0)
                    ss = u"执行重做"
                    return ss
                else:
                    status = OrderStatus.failure
                    DisOrder.update_status(order_id, status)
                    ss = u"执行重做失败"
                    return ss
            else:
                ss = u"输入正确订单号"
                return ss


