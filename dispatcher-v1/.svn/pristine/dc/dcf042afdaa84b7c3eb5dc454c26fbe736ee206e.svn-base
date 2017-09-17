# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
weilia
租户资源管理services
"""
from datetime import datetime

from flask import current_app
from flask import g
from flask import json

from app.catalog.public_ip.models import CmdbInternetIp
from app.catalog.public_ip.services import PublicIpService
from app.catalog.vpc.models import NetVpc
from app.configs.api_uri import biz
from app.configs.api_uri import network
from app.configs.api_uri import user
from app.configs.code import ResponseCode
from app.extensions import db
from app.management.logicpool.constant import PoolProperty
from app.management.logicpool.models import InfPoolTenantRef, InfLogicPool
from app.order.constant import OrderStatus, ResourceType
from app.order.models import DisOrderLog, DisOrder
from app.order.services import DisOrderService, DisOrderLogService
from app.security.member.services import SecurityService
from app.service_ import CommonService
from app.utils import helpers
from app.utils.database import model_to_dict
from app.utils.format import format_result
from app.catalog.public_ip.models import NetVpn


class TenantResourceService(CommonService):
    """
    weilai
    租户资源管理services
    """

    @staticmethod
    def get_tenant_list(args):
        """
        调取租户模块接口，查询租户列表
        :param args:
        :return:
        """
        uri = user.get_full_uri(user.TENANT_LIST)
        current_app.logger.info(u"查询租户列表，URI:{}".format(uri))
        args['current_page'] = args['page']
        status, datas, content = g.request(uri=uri, method='POST', body=helpers.json_dumps(args))
        current_app.logger.info(u"查询租户列表，返回值status:{}，data:{}".format(status, datas))
        # 返回值为json，循环取出租户id，查询与其关联的pool,封装返回列表
        if status:
            page = content['page']
            if datas:
                len_ = len(datas) - 1
                for k, i in enumerate(datas):
                    tenant_id = i['id']
                    # 查询资源池信息
                    pool = TenantResourceService.get_pool_by_tenant(tenant_id)
                    current_app.logger.info(u"查询租户关联的资源池列表，tenant_id:{},返回值pool:{}".format(tenant_id,pool))
                    i['pool'] = pool
                    # 查询安全服务信息
                    data_security = TenantResourceService.get_security_by_tenant(tenant_id)
                    current_app.logger.info(u"查询租户关联的安全服务，tenant_id:{},data_security:{}".format(tenant_id, data_security))
                    i['security'] = data_security
                    # 查询公网ip的数量
                    ip_number = TenantResourceService.get_ip_number_by_tenant(tenant_id)
                    current_app.logger.info(u"查询租户关联的公网ip的数量，tenant_id:{},ip_number:{}".format(tenant_id, ip_number))
                    i['ip_number'] = ip_number
                    # 查询vpc
                    vpc = TenantResourceService.get_vpc_by_tenant(tenant_id)
                    current_app.logger.info(u"查询租户关联的vpc，tenant_id:{},vpc:{}".format(tenant_id, vpc))
                    i['vpc'] = vpc
                    # 查询业务名称
                    status, biz_name = TenantResourceService.get_biz_by_tenant(tenant_id)
                    current_app.logger.info(u"查询租户关联的业务名称，tenant_id:{},biz_name:{}".format(tenant_id, biz_name))
                    i['approval'] = biz_name
                    if k == len_:
                        break
                return datas, page
            else:
                return datas, page
        else:
            current_app.logger.info(u"访问user系统错误")
            return 1, None

    @staticmethod
    def get_pool_by_tenant(tenant_id):
        """
        通过租户id查资源池
        :param tenant_id:
        :return:
        """
        # 查询资源池信息
        data_pool = InfPoolTenantRef.get_pool_by_tenant_id(tenant_id)
        data_pool = format_result(data_pool)
        pool_list = []
        if data_pool:
            for j in data_pool:
                pool_dict = dict()
                pool_name = j['name']
                location = j['location']
                pool_id = j['id']
                virtualtype = j['virtualtype']
                owner = j['owner']
                sla = j['sla']
                status = j['status']
                location_pool = location + u'/' + pool_name
                pool_dict['location'] = location
                pool_dict['pool_name'] = pool_name
                pool_dict['pool_id'] = pool_id
                pool_dict['location_pool'] = location_pool
                pool_dict['virtualtype'] = virtualtype
                pool_dict['ower'] = owner
                pool_dict['sla'] = sla
                pool_dict['status'] = status
                pool_list.append(pool_dict)
        return pool_list

    @staticmethod
    def get_security_by_tenant(tenant_id):
        """
        通过租户id查询安全服务信息
        :param tenant_id:
        :return:
        """
        tenant_args = dict()
        tenant_args['tenant_id'] = tenant_id
        data_security = SecurityService.security_list_by_tenant(tenant_args)
        if data_security:
            data_security = data_security
        else:
            data_security = []
        return data_security

    @staticmethod
    def get_ip_number_by_tenant(tenant_id):
        """
        通过租户id查询ip_number
        :param tenant_id:
        :return:
        """
        from app.catalog.public_ip.models import MappingResTenantRef
        ip_number = MappingResTenantRef.get_ipcount_by_tenant(tenant_id)
        ip_number = format_result(ip_number)
        if ip_number:
            ip_number = ip_number[0]['count(*)']
        else:
            ip_number = 0
        return ip_number

    @staticmethod
    def get_vpc_by_tenant(tenant_id):
        """
        通过租户id查询vpc
        :param tenant_id:
        :return:
        """
        vpc_list = []
        vpc = NetVpc.query.filter(NetVpc.tenant_id == tenant_id, NetVpc.removed.is_(None)).all()
        if vpc:
            vpc = [model_to_dict(v) for v in vpc]
            for i in vpc:
                vpc_name = i['vpc_name']
                client_pool_id, vpc_name = vpc_name.split('_', 1)
                i['vpc_name'] = vpc_name
                vpc_list.append(i)
        return vpc_list

    @staticmethod
    def get_biz_by_tenant(tenant_id):
        """
        通过租户id查询业务名称
        :param tenant_id:
        :return:
        """
        args = dict()
        args['tenant_id'] = tenant_id
        uri = biz.get_full_uri(biz.TENANT_BIZ_URI)
        current_app.logger.info(u"查询租户业务名称，URI:{}".format(uri))
        status, data, content = g.request(uri=uri, method='POST', body=helpers.json_dumps(args))
        current_app.logger.info(u"查询租户业务名称，返回值status:{}".format(status))
        if status:
            biz_data = data
            return status, biz_data
        else:
            biz_data = []
            current_app.logger.error(u"调用业务接口失败")
            return status, biz_data

    @staticmethod
    def get_zone_pool_list():
        """
        查询zone下的资源池列表，封装树状结构
        :return:
        """
        from app.management.zone.models import InfZone
        list_ = []
        zone_list = InfZone.get_enable_zone_list()
        zone_list = format_result(zone_list)
        if zone_list:
            for i in zone_list:
                data = dict()
                zone_id = i['id']
                zone_location = i['location']
                pool_list = InfLogicPool.get_pool_by_zone(zone_id)
                pool_list = format_result(pool_list)
                data['zone_location'] = zone_location
                data['zone_id'] = zone_id
                data['pool_list'] = pool_list
                list_.append(data)
        return list_

    @staticmethod
    def created_tenant_resource(args, commit=True):
        """
         租户资源管理（绑定公网IP，创建VPC，关联资源池，添加安全服务列表）
        :param args:
        :param commit:
        :return:
        """
        # 如果未关联，增加关联

        InfPoolTenantRef.created_pool_tenant(args)
        commit and db.session.commit()

    @staticmethod
    def judge_param(param):
        """
        判断参数是否合法，是否已产生关联,是否增加公网ip
        :param param:
        :return:
        """
        from app.catalog.public_ip.models import MappingResTenantRef
        tenant_id = param['tenant_id']
        ip_number = param['ip_number']
        location = param['location']
        pool_id = param['pool_id']
        security_services_id = param['security_services_id']
        safety_flag = param['safety_flag']
        # 查询该租户公网ip个数,如果没有为0
        count = MappingResTenantRef.get_ipcount_by_tenant(tenant_id)
        count = format_result(count)
        count = count[0]['count(*)']
        a = int(ip_number) - int(count)
        param['ip_number'] = a
        # 分配公网ip需要检查localtion
        if (location == '' or not location) and a != 0:
            param = u"关联客户资源池后才可分配公网ip"
            return False, param
        vpn = NetVpn.check_tenant_vpn(tenant_id)
        vpn = format_result(vpn)
        # 创建vpn也需要检查localtion
        if (location == '' or not location) and not (vpn or safety_flag == 1 or safety_flag == u'1'):
            current_app.logger.error(u"关联客户资源池后才可自动创建vpn")
            param = u"关联客户资源池后才可自动创建vpn"
            return False, param
        # 查询公网ip数量
        free_ip = CmdbInternetIp.get_num_free_int_ip(location)
        free_ip = format_result(free_ip)
        if free_ip:
            if len(free_ip) < a:
                current_app.logger.error(u"公网ip已不足，剩余:{},需要:{}".format(str(len(free_ip)),str(a)))
                param = str(location) + u"，公网IP已不足"+str(a)+u"个"+u"，目前剩余"+str(len(free_ip))+u"个"
                return False, param
        if not free_ip and a != 0:
            # 公网ip数量为0
            current_app.logger.error( u"location:{}，尚无公网ip，请先添加公网ip".format(location))
            param = str(location) + u"尚无公网IP,请先添加"
            return False, param
        if a < 0:
            current_app.logger.error(u"租户不可减少公网ip")
            param = u"租户不可减少公网ip"
            return False, param
        if pool_id:
            pool = InfPoolTenantRef.check_pool_tenant_ref(tenant_id, pool_id)
            pool = format_result(pool)
            # 如果已经关联，返回失败
            if pool:
                current_app.logger.error(u"已关联客户资源池不可再次关联")
                param = u"已关联客户资源池不可再次关联"
                return False, param
            # 检查已关联的资源池zone地址
            zone_list = InfPoolTenantRef.get_pool_by_tenant_id(tenant_id)
            zone_list = format_result(zone_list)
            # 查询要添加的资源池zone_id
            pool_detail = InfLogicPool.get_pool_by_pool_id(pool_id)
            pool_detail = format_result(pool_detail)
            pool_zone_id = pool_detail[0]['zone_id']
            if zone_list:
                for z in zone_list:
                    zone_id = z['zone_id']
                    if zone_id != pool_zone_id:
                        current_app.logger.error(u"租户关联客户资源池不可跨zone")
                        param = u"租户关联客户资源池不可跨zone"
                        return False, param
        if security_services_id:
            security = SecurityService.list_by_tenant_and_security(param)
            # 如果已经关联，返回失败
            if security == False:
                current_app.logger.error(u"已关联安全服务项不可再次关联")
                param = u"已关联安全服务项不可再次关联"
                return False, param
        current_app.logger.info(u"租户资源管理参数正确:{}".format(param))
        skip_node_list = TenantResourceService.judge_skip_node(param)
        if len(skip_node_list) == 5:
            current_app.logger.info(u"租户资源无改动，请重新确认")
            param = u" 租户资源无改动，请重新确认"
            return False, param
        current_app.logger.info(u"正确的，租户资源管理参数:{}".format(param))
        return True, param

    @staticmethod
    def judge_skip_node(order_apply_info):
        """
        判断是否需要跳过节点
        :param param:
        :return:
        """
        virtualtype = order_apply_info['virtualtype']
        ip_number = order_apply_info['ip_number']
        pool_id = order_apply_info['pool_id']
        tenant_id = order_apply_info['tenant_id']
        safety_flag = order_apply_info['safety_flag']
        security_services_id = order_apply_info['security_services_id']
        # 四个节点： 1,公网ip 2.安全服务项 3.project 4.vpc
        skip_node_list = []
        if ip_number == 0:
            # 跳过公网ip的节点
            skip_node_list.append(1)
        if security_services_id == u'':
            skip_node_list.append(2)
        # if pool_id == u'':
        #     # 跳过创建project和vpc节点
        #     skip_node_list.append(3)
        #     skip_node_list.append(4)
        # if pool_id and virtualtype == PoolProperty.vmware:
        #     # 跳过公网ip及创建project节点
        #     skip_node_list.append(3)
        # skip_node_list.append(1)
        # skip_node_list.append(2)
        skip_node_list.append(3)
        if pool_id == u'' or not pool_id:
            # 跳过创建project和vpc节点
            skip_node_list.append(5)
        vpn = NetVpn.check_tenant_vpn(tenant_id)
        vpn = format_result(vpn)
        # 创建过VPN 或 是内部租户则跳过创建 VPN节点
        if vpn or safety_flag == 1 or safety_flag == u'1':
            # 跳过创建VPN节点
            skip_node_list.append(4)
        return skip_node_list

    @staticmethod
    def pool_ref_tenant_task(param):
        """
        调用task方法
        :param param:
        :return:
        """
        # 1.生成订单 2.生成订单日志 3.判断是否分配公网ip 4.判断是否关联安全服务 5.调用编排流程（vpc/vpn）
        # 修改 直接跳过1,2,3节点的同步任务
        # 检查是否需要跳过节点，返回需要跳过节点的数组（）
        skip_node_list = TenantResourceService.judge_skip_node(param)
        current_app.logger.info(u"跳过节点列表:{}".format(skip_node_list))
        param['resource_type'] = ResourceType.Logic_Pool.value
        param['operation_type'] = u'tenant_resource'
        param['application_id'] = None
        apply_info = dict()
        apply_info['name_en'] = param['name_en']
        apply_info['pool_id'] = param['pool_id']
        apply_info['virtualtype'] = param['virtualtype']
        apply_info['ip_number'] = param['ip_number']
        apply_info['security_services_id'] = param['security_services_id']
        apply_info['tenant_name'] = param['tenant_name']
        apply_info['tenant_id'] = param['tenant_id']
        apply_info['location'] = param['location']
        apply_info['safety_flag'] = param['safety_flag']
        param['apply_info'] = apply_info
        current_app.logger.info(u"租户资源管理参数:{}".format(param))
        # 生成订单，超管的租户id为0
        param['tenant_id'] = 0
        order_id, serial_number = DisOrderService.create_order(param, commit=False)
        param['tenant_id'] = apply_info['tenant_id']
        current_app.logger.info(u"创建订单参数:{},订单id:{}".format(param, order_id))
        apply_info['order_id'] = order_id
        # 把order_id放到apply_info中
        DisOrderService.update_apply_info(order_id, apply_info, commit=False)
        # # 生成订单日志
        # order_log_args = dict()
        # order_log_args['operation_object'] = param['tenant_name']
        # order_log_args['operation_name'] = u"create_order"
        # order_log_args['execution_status'] = OrderStatus.doing
        # order_log_args['order_id'] = order_id
        # DisOrderLogService.created_order_log(order_log_args, commit=True)
        # current_app.logger.info(u"创建订单日志:{}".format(order_log_args))
        # order_log_args['execution_status'] = OrderStatus.succeed
        # # 生成订单成功
        # DisOrderLogService.created_order_log(order_log_args, commit=True)
        # current_app.logger.info(u"创建订单日志")

        # 3.判断是否分配公网ip
        # TenantResourceService.public_ip_tenant(apply_info, order_id)
        # # 4.判断是否关联安全服务
        # TenantResourceService.security_service_tenant(apply_info, order_id)
        # 走编排（创建vpc的编排）
        from app.process.task import TaskService
        result1 = TaskService.create_task(order_id, skip_node_list)
        current_app.logger.info(u"创建编排:{}".format(result1[1]))
        if result1[0] and result1[1] == '成功':
            result2 = TaskService.start_task(order_id,0)
            current_app.logger.info(u"开始编排流程:{}".format(result2 [1]))
            if result2[0]:
                current_app.logger.info(u"租户资源管理成功")
                return True, serial_number
            else:
                current_app.logger.info(u"租户资源管理失败，部分资源未添加成功，请根据订单重做")
                return False, serial_number

    @staticmethod
    def check_tenant(param):
        """
        检查该租户下是否有未完成的订单
        :return:
        """
        tenant_name = param['name_en']
        data = DisOrderLog.check_tenant_order(tenant_name)
        data = format_result(data)
        list_ = []
        if data:
            for i in data:
                # if i['apply_info'] != u"{}":
                #     apply_info = json.loads(i['apply_info'])
                #     pool_id1 = apply_info['pool_id']
                #     if pool_id1 == pool_id:
                serial_number = i['serial_number']
                list_.append(serial_number)
            return False, list_
        else:
            return True, list_

    @staticmethod
    def public_ip_tenant(order_apply_info, order_id):
        """
        给租户分配公网ip
        :param order_apply_info:
        :param order_id:
        :return:
        """
        if order_apply_info['ip_number'] > 0:
            args = dict()
            operation_object = order_apply_info['tenant_name']
            operation_name = u'bound_tenant_public_ip'
            execution_status = OrderStatus.doing
            args['operation_object'] = operation_object
            args['operation_name'] = operation_name
            args['execution_status'] = execution_status
            args['order_id'] = order_id
            DisOrderLogService.created_order_log(args, commit=True)
            current_app.logger.info(u"租户分配公网开始记录订单日志:{}！".format(args))
            number = order_apply_info['ip_number']
            order_apply_info['number'] = number
            uri = network.get_full_uri(network.Get_FREE_PUBLIC_IP)
            current_app.logger.info(u"调用network平台，查询空闲公网ip，参数:{},请求地址:{}".format(order_apply_info, uri))
            status, datas, content = g.request(uri=uri, method='post', body=order_apply_info)
            if status:
                current_app.logger.info(u"调用network平台，查询空闲公网ip:{}，返回结果:{}！".format(u"成功", datas))
                # 完成任务，删除记账表，绑定公网ip与租户关系，更改ip状态
                PublicIpService.bound_tenant_ip(order_apply_info, datas, commit=True)
                # 增加订单与资源的关系
                order_res = dict()
                order_res['resource_type'] = ResourceType.PUBLIC_IP.value
                for i in datas:
                    resource_id = i['id']
                    order_res['resource_id'] = resource_id
                    DisOrder.insert_order_ref(order_res)
                # 再次创建订单日志（完成）
                args_end = dict()
                execution_status = OrderStatus.succeed
                args_end['operation_object'] = operation_object
                args_end['operation_name'] = operation_name
                args_end['execution_status'] = execution_status
                args_end['order_id'] = order_id
                DisOrderLogService.created_order_log(args_end, commit=True)
            else:
                current_app.logger.info(u"调用network平台，查询空闲公网ip:{}（可能没有相应ip）！".format(u"失败"))
                args_end = dict()
                execution_status = OrderStatus.failure
                args_end['operation_object'] = operation_object
                args_end['operation_name'] = operation_name
                args_end['execution_status'] = execution_status
                args_end['order_id'] = order_id
                DisOrderLogService.created_order_log(args_end, commit=True)
        else:
            current_app.logger.info(u"租户不需要公网ip，订单order_id:{}，详情:{}！".format(order_id, order_apply_info))

    @staticmethod
    def security_service_tenant(order_apply_info, order_id):
        """
        关联安全服务项
        :param order_apply_info:
        :param order_id:
        :return:
        """
        if order_apply_info['security_services_id'] != u'':
            # 创建订单日志（开始）
            args = dict()
            operation_object = order_apply_info['tenant_name']
            operation_name = u'create_tenant_security_services'
            execution_status = OrderStatus.doing
            args['operation_object'] = operation_object
            args['operation_name'] = operation_name
            args['execution_status'] = execution_status
            args['order_id'] = order_id
            DisOrderLogService.created_order_log(args, commit=True)
            current_app.logger.info(u"租户关联安全服务项开始记录订单日志:{}！".format(args))
            # 完成节点，增加安全服务的关联关系
            ss = SecurityService.insert_tenant_security(order_apply_info, commit=True)
            if ss:
                current_app.logger.info(u"关联安全服务项状态:{}！".format(u"成功"))
                # 增加订单与资源的关系
                order_res = dict()
                order_res['order_id'] = order_id
                order_res['resource_type'] = ResourceType.SECURITY_SERVICES.value
                for i in order_apply_info['security_services_id'].split(','):
                    order_res['resource_id'] = i
                    DisOrder.insert_order_ref(order_res)
                current_app.logger.info(u"增加订单与安全服务项关联关系！")
                # 再次创建订单日志（完成）
                args_end = dict()
                execution_status = OrderStatus.succeed
                args_end['operation_object'] = operation_object
                args_end['operation_name'] = operation_name
                args_end['execution_status'] = execution_status
                args_end['order_id'] = order_id
                DisOrderLogService.created_order_log(args_end, commit=True)
                current_app.logger.info(u"租户关联安全服务项成功记录订单日志:{}！".format(args_end))
            else:
                current_app.logger.info(u"关联安全服务项状态:{}！".format(u"失败"))
                args_end = dict()
                execution_status = OrderStatus.failure
                args_end['operation_object'] = operation_object
                args_end['operation_name'] = operation_name
                args_end['execution_status'] = execution_status
                args_end['order_id'] = order_id
                DisOrderLogService.created_order_log(args_end, commit=True)
                current_app.logger.info(u"租户关联安全服务项失败订单日志:{}！".format(args_end))
        else:
            current_app.logger.info(u"租户不需要关联安全服务项，订单order_id:{}，详情:{}！".format(order_id, order_apply_info))
