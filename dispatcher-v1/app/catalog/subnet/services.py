# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-1-4

    Subnet 服务层相应方法
"""
from IPy import IP
from flask import current_app, g

from app.configs.code import ResponseCode
from app.service_ import CommonService
from app.catalog.vpc.models import NetVpc
from app.catalog.subnet.models import CmdbIpSegment
from app.utils.database import model_to_dict
from app.utils.format import format_result2one
from app.utils.response import res, res_details


class SubnetService(CommonService):
    @classmethod
    def create_os_subnet(cls, args):
        """
            sxw 2017-1-12

            创建openstack子网信息
        """
        # vpc_id是否存在
        error_msg = u"不存在此vpc信息，请重试!"
        vpc = NetVpc.query.get(args["vpc_id"])
        if vpc:
            # 网关是否在网段地址中
            error_msg = u"输入错误，网关地址不在网段中!"
            # 已修改 2017/2/3weilai 备注 args("segment"),args("gateway") 语法错误
            segment = IP(args["segment"])
            if segment.overlaps(args["gateway"]) == 1:
                # 校验子网名称是否重复
                error_msg = u"该子网名字已经被占用，请重试!"
                from app.catalog.subnet.models import NetSubnet
                subnet = NetSubnet.query.join(NetVpc, NetSubnet.vpc_id == NetVpc.id).filter(
                    NetSubnet.name == args["name"], NetVpc.id == vpc.id,
                    NetSubnet.removed.is_(None)).first()
                if not subnet:
                    error_msg = u"该子网网段已经被占用，请重试!"
                    subnet = NetSubnet.query.join(CmdbIpSegment, CmdbIpSegment.id == NetSubnet.segment_id).filter(
                        NetSubnet.removed.is_(None), NetSubnet.vpc_id == vpc.id,
                        CmdbIpSegment.segment == segment.net().strFullsize(),
                        CmdbIpSegment.mask == segment.netmask().strFullsize()
                    ).first()
                    if not subnet:
                        # # 查询记账表，网段是否被占用
                        # error_msg = u"该网段已经被占用，请重试!"
                        # from app.catalog.public_ip.models import DisResourceAllocate
                        # from app.catalog.subnet.models import CmdbIpSegment
                        # resource_allocate = DisResourceAllocate.query.join(CmdbIpSegment,
                        #                                                    CmdbIpSegment.id ==
                        #                                                    DisResourceAllocate.resource_id). \
                        #     filter(DisResourceAllocate.allocate_type == 'NET_SEGMENT',
                        #            CmdbIpSegment.segment == segment.net().strNormal(),
                        #            CmdbIpSegment.mask == segment.netmask().strNormal()).first()

                        vpc_name = vpc.vpc_name
                        tenant_id = vpc.tenant_id
                        logic_pool_id, _ = vpc_name.split('_')
                        from app.management.logicpool.models import InfLogicPool
                        from app.management.logicpool.models import InfPoolTenantRef
                        logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                             InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
                            InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                                InfLogicPool.removed.is_(None),
                                                                InfPoolTenantRef.tenant_id == tenant_id).first()
                        error_msg = u"数据库中数据错误，查询对应资源池id={}，租户id={}失败，请联系管理员！".format(logic_pool_id, tenant_id)

                        # 若数据库中数据错误，则记录错误日志信息
                        if not logic_pool:
                            current_app.logger.error(error_msg)

                        if logic_pool:
                            logic_pool, project_id = logic_pool
                            logic_pool = model_to_dict(logic_pool)
                            operation_object = g.tenant.get("name_en")
                            operation_name = "create_vpc_subnet"

                            # 创建订单
                            args.update({"pool_{}".format(k): v for k, v in logic_pool.items()})
                            args["hypervisor_type"] = vpc.hypervisor_type
                            args["project_id"] = project_id
                            args["tenant_id"] = vpc.tenant_id
                            args["logic_pool_id"] = logic_pool_id
                            args["operation_object"] = operation_object
                            args["operation_name"] = operation_name
                            from app.order.constant import ResourceType
                            order_d = {"user_id": g.user.get("current_user_id"), "tenant_id": g.tenant.get("tenant_id"),
                                       "application_id": "", "application_name": "",
                                       "resource_type": ResourceType.Sub_Net.value, "operation_type": u"create",
                                       "apply_info": args}
                            from app.order.services import DisOrderService
                            order_id, serial_number = DisOrderService.create_order(order_d, commit=True)

                            # 创建订单日志
                            from app.order.constant import OrderStatus
                            from app.order.services import DisOrderLogService
                            order_log_d = {"operation_object": operation_object,
                                           "operation_name": operation_name,
                                           "execution_status": OrderStatus.doing,
                                           "order_id": order_id}
                            DisOrderLogService.created_order_log(order_log_d, commit=True)

                            # 创建task
                            from app.process.task import TaskService
                            alloc_result = TaskService.create_task(order_id)
                            error_msg = u"创建VPC子网失败!"
                            if alloc_result[1] == u'成功':
                                TaskService.start_task(order_id)
                                # error_msg = u""
                                return True, serial_number

        return False, error_msg

    @classmethod
    def create_vm_subnet(cls, args):
        """
            sxw 2017-1-16

            创建vmware子网信息
        """
        # vpc_id是否存在
        error_msg = u"不存在此vpc信息，请重试!"
        vpc = NetVpc.query.get(args["vpc_id"])
        if vpc:
            # segment_id是否存在
            error_msg = u"不存在此网段信息或此网段非空闲状态，请重试!"
            from app.catalog.subnet.models import CmdbIpSegment
            ip_segment = CmdbIpSegment.query.filter(CmdbIpSegment.id == args["segment_id"],
                                                    CmdbIpSegment.status == u"空闲").first()
            if ip_segment:
                error_msg = u"此网段已被占用，请重试!"
                from app.catalog.public_ip.models import DisResourceAllocate
                resource_allocate = DisResourceAllocate.query.join(CmdbIpSegment,
                                                                   CmdbIpSegment.id ==
                                                                   DisResourceAllocate.resource_id). \
                    filter(DisResourceAllocate.allocate_type == 'NET_SEGMENT',
                           CmdbIpSegment.id == args["segment_id"]).first()
                if not resource_allocate:
                    # 校验子网名称是否重复
                    error_msg = u"该子网名字已经被占用，请重试!"
                    from app.catalog.subnet.models import NetSubnet
                    subnet = NetSubnet.query.filter(NetSubnet.name == args["name"],
                                                    NetSubnet.removed.is_(None),
                                                    NetSubnet.vpc_id == vpc.id).first()
                    if not subnet:
                        vpc_name = vpc.vpc_name
                        logic_pool_id, _ = vpc_name.split('_')
                        from app.management.logicpool.models import InfLogicPool
                        from app.management.logicpool.models import InfPoolTenantRef
                        logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                             InfLogicPool.id == InfPoolTenantRef.pool_id).filter(
                            InfLogicPool.id == logic_pool_id,
                            InfLogicPool.removed.is_(None),
                            InfPoolTenantRef.tenant_id == vpc.tenant_id).first()
                        error_msg = u"数据库中数据错误，查询对应资源池id={}，租户id={}失败，请联系管理员！".format(logic_pool_id, vpc.tenant_id)

                        # 若数据库中数据错误，则记录错误日志信息
                        if not logic_pool:
                            current_app.logger.error(error_msg)

                        if logic_pool:
                            logic_pool = model_to_dict(logic_pool)
                            operation_object = g.tenant.get("name_en")
                            operation_name = "create_vpc_subnet"

                            # 创建订单
                            args.update({"pool_{}".format(key): value for key, value in logic_pool.items()})
                            args.update({"vpc_{}".format(k) if not k.startswith('vpc_') else k: v for k, v in
                                         model_to_dict(vpc).items()})
                            args.update({"ip_segment_{}".format(k): v for k, v in model_to_dict(ip_segment).items()})
                            args["tenant_id"] = g.tenant.get("tenant_id")
                            args["hypervisor_type"] = vpc.hypervisor_type
                            args["logic_pool_id"] = logic_pool_id
                            args["operation_object"] = operation_object
                            args["operation_name"] = operation_name
                            from app.order.constant import ResourceType
                            order_d = {"user_id": g.user.get("current_user_id"), "tenant_id": g.tenant.get("tenant_id"),
                                       "application_id": "", "application_name": "",
                                       "resource_type": ResourceType.Sub_Net.value, "operation_type": u"create",
                                       "apply_info": args}
                            from app.order.services import DisOrderService
                            order_id, serial_number = DisOrderService.create_order(order_d, commit=True)

                            # 创建订单日志
                            from app.order.constant import OrderStatus
                            from app.order.services import DisOrderLogService

                            order_log_d = {"operation_object": operation_object,
                                           "operation_name": operation_name,
                                           "execution_status": OrderStatus.doing,
                                           "order_id": order_id}
                            DisOrderLogService.created_order_log(order_log_d, commit=True)

                            # 创建task
                            from app.process.task import TaskService
                            alloc_result = TaskService.create_task(order_id)
                            error_msg = u"创建VPC子网失败!"
                            if alloc_result[1] == u'成功':
                                TaskService.start_task(order_id)
                                # error_msg = u""
                                return True, serial_number

        return False, error_msg

    @staticmethod
    def get_segment_by_mask(args):
        """
            zhouming 2016-12-26

            通过地址空闲选择segment
        """
        # 地址空间
        address_space = args['mask']
        from app.utils.helpers import exchange_mask_int
        _mask = exchange_mask_int(address_space)
        # 查询
        result = CmdbIpSegment.get_segment_by_mask(_mask)
        result_segment = format_result2one(result)
        if result_segment:
            return res_details(data=result_segment)
        else:
            error_msg = u'vmware网段资源不足'
            current_app.logger.error(error_msg)
            return res(code=ResponseCode.ERROR, msg=error_msg)

    @staticmethod
    def delete_subnets(subnets):
        """
            songxiaowei 2017-2-16

            多删除子网信息
        """
        error_msg = u""
        serial_numbers = []
        order_ids = []
        # 迭代删除子网
        for subnet in subnets:
            vpc = NetVpc.query.get(subnet.vpc_id)
            vpc_name = vpc.vpc_name
            logic_pool_id, _ = vpc_name.split('_')
            from app.management.logicpool.models import InfLogicPool
            from app.management.logicpool.models import InfPoolTenantRef
            logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                 InfLogicPool.id == InfPoolTenantRef.pool_id). \
                add_columns(InfPoolTenantRef.project_id).filter(
                InfLogicPool.id == logic_pool_id,
                InfLogicPool.removed.is_(None),
                InfPoolTenantRef.tenant_id == vpc.tenant_id).first()
            error_msg = u"数据库中数据错误，查询对应资源池id={}，租户id={}失败，请联系管理员！". \
                format(logic_pool_id, vpc.tenant_id)

            # 若数据库中数据错误，则记录错误日志信息
            if not logic_pool:
                current_app.logger.error(error_msg)

            if logic_pool:
                logic_pool, project_id = logic_pool
                logic_pool = model_to_dict(logic_pool)
                operation_object = g.tenant.get("name_en")
                operation_name = "delete_vpc_subnet"

                # 创建订单
                apply_info = {"pool_{}".format(key): value for key, value in logic_pool.items()}
                apply_info.update({"vpc_{}".format(k) if k.startswith('vpc_') else k: v for k, v in
                                   model_to_dict(vpc).items()})
                apply_info["subnet_id"] = subnet.id
                apply_info["segment_id"] = subnet.segment_id
                apply_info["hypervisor_type"] = vpc.hypervisor_type
                apply_info["logic_pool_id"] = logic_pool_id
                apply_info["operation_object"] = operation_object
                apply_info["operation_name"] = operation_name
                apply_info["project_id"] = project_id
                from app.order.constant import ResourceType
                order_d = {"user_id": g.user.get("current_user_id"), "tenant_id": g.tenant.get("tenant_id"),
                           "application_id": "", "application_name": "",
                           "resource_type": ResourceType.Sub_Net.value, "operation_type": u"delete",
                           "apply_info": apply_info}
                from app.order.services import DisOrderService
                order_id, serial_number = DisOrderService.create_order(order_d, commit=True)

                # 创建订单日志
                from app.order.constant import OrderStatus
                from app.order.services import DisOrderLogService

                order_log_d = {"operation_object": operation_object,
                               "operation_name": operation_name,
                               "execution_status": OrderStatus.doing,
                               "order_id": order_id}
                DisOrderLogService.created_order_log(order_log_d, commit=True)

                # 创建task
                from app.process.task import TaskService
                alloc_result = TaskService.create_task(order_id)
                error_msg = u"删除VPC子网失败, vpc子网名称为:{}!".format(subnet.name)
                if alloc_result[1] == u'成功':
                    error_msg = u""
                    serial_numbers.append(serial_number)
                    order_ids.append(order_id)

                if error_msg:
                    break

        if error_msg:
            return False, error_msg

        # 没有错误情况，迭代启动异步任务
        for order_id in order_ids:
            TaskService.start_task(order_id)
        return True, ','.join(serial_numbers)
