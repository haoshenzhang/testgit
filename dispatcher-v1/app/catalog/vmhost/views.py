#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from flask import g,current_app,session
from flask_restful import reqparse, Resource

from app.cmdb.cossmap import coss_host_mapping
from app.cmdb.vm.models import CmdbHostLogicserver
from app.cmdb.vm.service import VMRecoverCMDB, VMTakeOverCMDB
from app.deployment.models import ComAsyncTask
from app.extensions import back_ground_scheduler
from app.order.constant import OrderStatus
from app.order.models import DisOrderLog
from app.order.services import DisOrderService, DisOrderLogService
from app.configs.code import ResponseCode
from app.catalog.vmhost.services import VMService
from app.utils.my_logger import log_decorator, ActionType,ResourceType as Resourcetype
from app.utils.response import res,res_list_page
from app.utils.parser import common_parser
from app.catalog.vmhost.models import Dis_Offering,Dis_Os_Template
from flask import request


# 参数解析对象生成
from app.utils.rest_client import RestClient

parser = reqparse.RequestParser()
common_parser(parser)


class VMHostApi(Resource):
    """
    虚机新建API
    """

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=Resourcetype.vm.value)
    def post():
        useless = ['o_names','q_names','q_values','per_page','q_type','o_values','page']
        order_args_list = ['application_id','operation_type','application_name'] + useless
        apply_args_list = ['number','os','private_net_name','password','description',
                           'pool_id','offering_id','template_id','volumes','trustee','coss_id'] + useless
        parser_post = parser.copy()
        parser_post.add_argument("application_id", type=int, required=True)
        parser_post.add_argument('coss_id')
        parser_post.add_argument("application_name",required=True)
        parser_post.add_argument("resource_type", required=True)
        parser_post.add_argument("operation_type",type=str,required=True)
        parser_post.add_argument("number",type=int,required=True)
        parser_post.add_argument("os",type=str)
        parser_post.add_argument("private_net_name",required=True)              #子网id???
        parser_post.add_argument("password",required=True)
        parser_post.add_argument("description",type=str,required=True)
        parser_post.add_argument("pool_id",type=int,required=True)
        parser_post.add_argument('offering_id',required=True)
        parser_post.add_argument('template_id',type=int, required=True)
        parser_post.add_argument('volumes')
        parser_post.add_argument('trustee',type=int,required=True)
        volumes = request.json.get('volumes',None)
        volumes_dict = dict(volumes=volumes)
        args = parser_post.parse_args()
        #args['trustee'] = 0
        #if args['trustee'] == 1:
        #    args['operation_type'] = 'create_untrust'
        args['operation_type'] = 'create_untrust'
        #args['operation_type'] = 'create'
        if args['coss_id'] == None:
            args['coss_id'] = ''
        apply_info_args = args.copy()
        order_args = args.copy()
        for item in order_args_list:
            apply_info_args.pop(item)
            apply_info_args.update(volumes_dict)
        for order_item in apply_args_list:
            order_args.pop(order_item)
        order_args['apply_info'] = apply_info_args
        order_args['user_id'] = g.user['current_user_id']
        order_args['tenant_id'] = g.tenant['tenant_id']
        safety_flag = g.tenant.get("safety_flag", 0)
        apply_info_args['safety_flag'] = safety_flag
        orderid,serial_number = DisOrderService.create_order(order_args, commit=True)
        if orderid:
            current_app.logger.info(u"订单创建成功")
            task_result = VMService.create_vmhost(orderid)
            if task_result == u'SUCCESS':
                return res(ResponseCode.SUCCEED,data={"serial_number": serial_number})
            else:
                DisOrderService.update_order_status(orderid,OrderStatus.failure)
                return res(ResponseCode.ERROR,msg=u"创建错误，请联系管理员",data={"serial_number": serial_number})
        return res(code=ResponseCode.GET_BY_PARAM_ERROR, msg="创建订单失败，请检查参数是否正确")

    @staticmethod
    def get():
        parser_get = parser.copy()
        parser_get.add_argument("user_id", type=int, required=True)
        args = parser_get.parse_args()
        return res(code=ResponseCode.SUCCEED,msg='get_test')

class VMRemoveApi(Resource):
    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=Resourcetype.vm.value, id_name="vm_id_list")
    def post():
        """
        移除虚机 放入回收站
        :return:
        """
        parser_get = parser.copy()
        parser_get.add_argument("pool_id", type=int)
        args = parser_get.parse_args()
        vm_id_list = request.json.get('vm_id_list', None)
        vm_id_list = VMService.trans_vm_internal_id_to_id(vm_id_list)
        apply_info = None
        if vm_id_list:
            tmp_ = vm_id_list.split(',')
            number = len(tmp_)
            apply_info = dict(
                number=number,
                vm_id_list=vm_id_list,
                action = u'stop'
            )
        order_args = dict(
            resource_type=u'VM',
            operation_type=u'remove',
            apply_info=apply_info
        )
        order_args['user_id'] = g.user['current_user_id']
        order_args['tenant_id'] = g.tenant['tenant_id']
        orderid,serial_number = DisOrderService.create_order(order_args, commit=True)
        if orderid:
            VMService.vm_remove(vm_id_list=vm_id_list, order_id=orderid)
        return res(code=ResponseCode.SUCCEED, msg='SUCCEED',data={"serial_number": serial_number})

class VMRecoverApi(Resource):
    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.vm.value, id_name="vm_id_list")
    def post():
        """
        恢复虚机 从回收站里恢复
        :return:
        """
        parser_get = parser.copy()
        args = parser_get.parse_args()
        vm_id_list = request.json.get('vm_id_list', None)
        vm_id_list = str(vm_id_list)
        vm_id_list = VMService.trans_vm_internal_id_to_id(vm_id_list)
        apply_info = None
        if vm_id_list:
            tmp_ = vm_id_list.split(',')
            number = len(tmp_)
            apply_info = dict(
                number=number,
                vm_id_list=vm_id_list,
                action=u'start'
            )
        order_args = dict(
            resource_type=u'VM',
            operation_type=u'recover',
            apply_info=apply_info
        )
        order_args['user_id'] = g.user['current_user_id']
        order_args['tenant_id'] = g.tenant['tenant_id']
        orderid,serial_number = DisOrderService.create_order(order_args, commit=True)
        if orderid:
            VMRecoverCMDB.update_cmdb(orderid)
            DisOrderService.update_order_status(orderid,OrderStatus.succeed)
            order_log_dict = dict(
                order_id=orderid,
                operation_object='VM',
                operation_name='recover',
                execution_status=OrderStatus.doing
            )
            current_app.logger.info(u"插入订单日志")
            DisOrderLogService.created_order_log(order_log_dict)
            order_log_dict['execution_status'] = OrderStatus.succeed
            DisOrderLogService.created_order_log(order_log_dict)
            #VMService.vm_recover(vm_id_list=vm_id_list, order_id=orderid)
        return res(code=ResponseCode.SUCCEED, msg='SUCCEED',data={"serial_number": serial_number})


class VMDeleteApi(Resource):
    @staticmethod
    @log_decorator(action=ActionType.delete.value, resource=Resourcetype.vm.value,id_name="vm_id_list")
    def post():
        """
        真实 删除虚机操作
        :return:
        """
        parser_get = parser.copy()
        args = parser_get.parse_args()
        vm_id_list = request.json.get('vm_id_list', None)
        vm_id_list = str(vm_id_list)
        vm_id_list = VMService.trans_vm_internal_id_to_id(vm_id_list)
        vm_id_list_tmp = vm_id_list.split(',')
        flag = True
        for vm_item in vm_id_list_tmp:
            public_ip = VMService.check_vm_public_ip(vm_item)
            if not public_ip:
                flag = False
        if flag:
            safety_flag = g.tenant.get("safety_flag", 0)
            apply_info = None
            if vm_id_list:
                tmp_ = vm_id_list.split(',')
                number = len(tmp_)
                apply_info = dict(
                    number = number,
                    vm_id_list = vm_id_list,
                    safety_flag = safety_flag
                )
            order_args = dict(
                resource_type = u'VM',
                operation_type = u'delete',
                apply_info = apply_info,
                tenant_id = g.tenant['tenant_id'],
                user_id=g.user['current_user_id']
            )
            orderid,serial_number = DisOrderService.create_order(order_args, commit=True)
            if orderid:
                current_app.logger.info(u"创建订单成功,准备创建删除虚机流程")
                VMService.vm_delete(vm_id_list=vm_id_list,order_id=orderid)
            return res(code=ResponseCode.SUCCEED,msg='SUCCEED',data={"serial_number": serial_number})
        else:
            return res(code=ResponseCode.ERROR,msg=u"请先解绑公网IP")

class VMActionAPI(Resource):
    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.vm.value, id_name="vm_id_list")
    def post():
        """
        虚机操作api
        action 包括start, stop , reboot
        :return:
        """
        parser_post = parser.copy()
        vm_id_list = request.json.get('vm_id_list', None)
        vm_id_list = str(vm_id_list)
        vm_id_list = VMService.trans_vm_internal_id_to_id(vm_id_list)
        parser_post.add_argument("action",type=str,required=True)
        args = parser_post.parse_args()
        tmp_list = vm_id_list.split(',')
        vm_id_first = tmp_list[0]
        args_ = dict(
            vm_id=vm_id_first
        )
        vm_info = VMService.get_vm_info(args_)[0]
        application_id = vm_info['application_id']
        application_name = vm_info['application_name']
        operation_type = args['action']
        apply_info = None
        if vm_id_list:
            tmp_ = vm_id_list.split(',')
            number = len(tmp_)
            apply_info = dict(
                number = number,
                vm_id_list = vm_id_list,
                action = operation_type
            )
        order_args = dict(
            resource_type=u'VM',
            operation_type=args['action'],
            apply_info=apply_info,
            tenant_id=g.tenant['tenant_id'],
            user_id=g.user['current_user_id'],
            application_id=application_id,
            application_name=application_name
        )
        #order_args,hypervisor_type = VMService.pre_order_args(args)
        order_id, serial_number = DisOrderService.create_order(order_args, commit=True)
        if order_id:
            current_app.logger.info(u"虚机action创建订单成功，准备执行流程")
            VMService.vm_action(args=args,order_id=order_id)
            return res(code=ResponseCode.SUCCEED,data={"serial_number": serial_number})

class VMUpdateInfo(Resource):
    @staticmethod
    @log_decorator(action=ActionType.update.value, resource=Resourcetype.vm.value, id_name="vm_id")
    def post():
        """
        更新虚机操作信息
        名称与描述
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("vm_id", type=str, required=True)
        parser_post.add_argument("name",type=str,required=True)
        parser_post.add_argument("description",type=str,required=True)
        args = parser_post.parse_args()
        tenant_id = g.tenant['tenant_id']
        vm_name = args.get('name')
        vm_id = args.get('vm_id')
        vm_id = VMService.trans_vm_internal_id_to_id(vm_id)
        if VMService.check_vm_name(vm_id,vm_name,tenant_id):
            VMService.vm_update_info(args=args)
            return res(code=ResponseCode.SUCCEED)
        else:
            return res(code=ResponseCode.VALIDATE_FAIL,msg=u"虚机名称重复")

class VMUpdateOffering(Resource):
    @staticmethod
    def post():
        """
        虚机操作api
        action 包括start, stop , reboot
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("vm_id", type=int, required=True)
        parser_post.add_argument("offering")
        parser_post.add_argument("application")
        parser_post.add_argument("number")
        parser_post.add_argument("os_type")
        parser_post.add_argument("os_template")
        parser_post.add_argument("trustee")
        args = parser_post.parse_args()
        #VMService.vm_action(args=args)
        return res(code=ResponseCode.SUCCEED)

class VMOfferingApi(Resource):
    @staticmethod
    def get():
        """
        获取虚机配置
        :return:
        """
        config_list = Dis_Offering.query_vm_config()
        return res(ResponseCode.SUCCEED,data=config_list)


class VMTemplateApi(Resource):

    @staticmethod
    def get():
        """
        获取虚机模板信息
        :return:
        """
        parser_post = parser.copy()
        parser_post.add_argument("os_type")
        parser_post.add_argument("vm_type")
        args = parser_post.parse_args()
        template_list = VMService.vm_offering(args)
        return res(ResponseCode.SUCCEED,data=template_list)


class VMListApi(Resource):
    """
    获取当前租户下的虚机列表
    """
    @staticmethod
    def post():
        parser_get = parser.copy()
        parser_get.add_argument("pool_id", type=int)
        kargs = parser_get.parse_args()
        args = request.json
        args['tenant_id'] = g.tenant['tenant_id']
        args['pool_id'] = kargs.get('pool_id',None)
        page = args['current_page']
        recycle = int(args['recycle'])
        vm_list = VMService.get_vm_list(args)
        vm_count = VMService.get_vm_count(args)
        if not vm_list:
            vm_count = 0
        return res_list_page(ResponseCode.SUCCEED, u"SUCCESS", None, vm_list, vm_count, page)


class VMTakeOverApi(Resource):
    """
    虚机数据接管接口
    """
    @staticmethod
    def get():
        pass

    @staticmethod
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("vc_id")
        parser_post.add_argument("network_name")
        parser_post.add_argument("application_id")
        parser_post.add_argument("application_name")
        parser_post.add_argument("tenant_id")
        args = parser_post.parse_args()
        network_name = args['network_name']
        vc_id = args['vc_id']
        vms = VMService.take_over_vm_pre(vc_id, network_name)
        current_app.logger.info("vms数据为:{}".format(vms))
        current_app.logger.info("虚机个数:{}".format(len(vms)))
        number = len(vms)
        apply_info_dict = dict(
            number=number,
            vm_list=vms,
            application_id=args['application_id'],
            application_name=args['application_name'],
            tenant_id=args['tenant_id']
        )
        order_args = dict(
            resource_type=u'VM',
            operation_type=u'takeover',
            apply_info=apply_info_dict,
            tenant_id=g.tenant['tenant_id'],
            user_id=g.user['current_user_id']
        )
        order_id, serial_number = DisOrderService.create_order(order_args)
        if order_id:
            current_app.logger.info(u"虚机action创建订单成功，准备执行流程")
            VMService.take_over_vm(order_id=order_id)
            return res(code=ResponseCode.SUCCEED, data={"serial_number": serial_number})


class VMTestApi(Resource):
    @staticmethod
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("id")
        args = parser_post.parse_args()
        order_id = args['id']
        order_id = int(order_id)
        from app.process.task import TaskService
        c = TaskService.start_task(order_id)
        return res

    @staticmethod
    def get():
        num = 0
        vm_num = len(coss_host_mapping)
        # 未查到
        un = []
        # 不匹配
        un_ = []
        for item in coss_host_mapping:
            name = item.keys()[0]
            coss_id = item.values()[0]
            result = RestClient.query_by_id_instances(coss_id)
            if result:
                result = json.loads(result)
                ciname = result['values']['CiName'][8:]
                ciname = ciname.lower()
                current_app.logger.info(u"ciname:{}".format(ciname))
                if ciname == name:
                   num += 1
                else:
                  un.append(name)
            else:
                un_.append(name)
        if vm_num == num:
            current_app.logger.info(u"全部匹配")
        else:
            current_app.logger.info(u"不匹配")
        current_app.logger.info(u"不匹配列表:{}".format(un))
        current_app.logger.info(u"没查到:{}".format(un_))
        return res()

    @staticmethod
    def delete():
        from app.extensions import back_ground_scheduler
        back_ground_scheduler.delete_job(id='996')
        return res(ResponseCode.SUCCEED)

    @staticmethod
    def put():
        parser_post = parser.copy()
        parser_post.add_argument("id")
        args = parser_post.parse_args()
        order_id = args['id']
        order_id = int(order_id)
        from app.cmdb.vm.service import VMActionCMDB, VMDeleteCMDB, VMCMDB
        VMCMDB.update_cmdb(order_id)
        return res


