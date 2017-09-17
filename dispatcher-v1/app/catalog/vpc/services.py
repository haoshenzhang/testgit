# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2017-1-4

    vpc 服务层相应方法
"""
from flask import current_app, g

from app.extensions import db
from app.service_ import CommonService
from app.catalog.vpc.models import NetVpc
from app.utils.database import model_to_dict
from app.utils.format import format_result

from app.catalog.vpc.constant import split_vpc_name, combination_vpc_name


class VpcService(CommonService):
    @classmethod
    def check_vpc_name(cls, args):
        """
            sxw 2017-1-4

            校验vpc名称
        """
        data = NetVpc.check_vpc_name(args['vpc_name'])
        return format_result(data)

    @classmethod
    def create_vpc(cls, args):
        """
            sxw 2017-1-5

            创建vpc
        """
        error_msg = u"vpc_name已存在，请重试!"
        # weilai 2017/2/4  修改备注  原因：传值错误，应该传args
        vpc_object = cls.check_vpc_name(args)
        if not vpc_object:
            error_msg = u"此租户已经创建vpc，请重试!"
            from app.catalog.subnet.constant import SubnetStatus
            tenant_vpc = NetVpc.query.filter(NetVpc.tenant_id == args['tenant_id'], NetVpc.removed.is_(None),
                                             NetVpc.status.in_((SubnetStatus.normal.value,
                                                                SubnetStatus.executing.value))).first()
            if not tenant_vpc:
                #######################################
                current_app.logger.info(u"调用用户平台，查询租户相关信息开始！")
                # 请求用户平台，获取租户信息
                from app.configs.api_uri import user as user_
                # weilai 2017/2/4 备注 调用user模块接口不通
                tenant_uri = user_.get_full_uri(user_.TENANT_URI)
                status, data, content = g.request(uri="{}{}{}".format(tenant_uri, '/', args['tenant_id']), method='GET')
                if status:
                    current_app.logger.info(u"调用用户平台，查询租户相关信息结束，{}！".format(u"成功"))
                else:
                    error_msg = data if data else u"不存在此租户，请联系管理员!"
                    current_app.logger.error(u"调用用户平台，查询租户相关信息结束，{}！".format(error_msg))
                #######################################
                if status:
                    error_msg = u"此租户id={},name={}不存在此客户资源池id={}信息!".format(args.get("tenant_id"), data.get("name_zh"),
                                                                            args.get("logic_pool_id"))
                    from app.management.logicpool.models import InfLogicPool
                    from app.management.logicpool.models import InfPoolTenantRef
                    from app.management.zone.models import InfZone
                    # logic_pool = InfLogicPool.get_pool_by_pool_id(args.get("logic_pool_id"))
                    logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                         InfLogicPool.id == InfPoolTenantRef.pool_id) \
                        .join(InfZone, InfZone.id == InfLogicPool.zone_id).add_columns(InfPoolTenantRef.project_id,
                                                                                       InfZone.location).filter(
                        InfLogicPool.id == args.get("logic_pool_id"),
                        InfLogicPool.removed.is_(None),
                        InfPoolTenantRef.tenant_id == args.get("tenant_id")).first()
                    if logic_pool:
                        logic_pool, project_id, location = logic_pool
                        logic_pool = model_to_dict(logic_pool)
                        operation_object = data.get("name_zh")
                        operation_name = "create_vpc"
                        # 创建订单
                        args.update(logic_pool)
                        args["project_id"] = project_id
                        args["location"] = location
                        args["operation_object"] = operation_object
                        args["operation_name"] = operation_name
                        from app.order.constant import ResourceType
                        #  备注 weilai 2017/2/4 1.获取不到user，2. 管理员没有租户，g.tenant错误 3.application_id为str''，在创建订单时报错，
                        order_d = {"user_id": g.user.get("current_user_id"), "tenant_id": g.tenant.get("tenant_id"),
                                   "application_id": "", "application_name": "",
                                   "resource_type": ResourceType.VPC.value, "operation_type": u"create",
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
                        error_msg = u"创建VPC失败!"
                        if alloc_result[1] == u'成功':
                            TaskService.start_task(order_id)
                            # error_msg = u""
                            return True, serial_number

        return False, error_msg

    @classmethod
    def update_vpc(cls, args):
        error_msg = u"vpc_id不存在或无权限操作!"
        admin, tenant_admin, user = False, False, False
        if int(g.user["is_super"]):
            admin = True
        # elif g.tenant["is_admin"]:
        #     tenant_admin = True
        # else:
        #     user = True
        net_vpc_query = NetVpc.query.filter(NetVpc.id == args["vpc_id"], NetVpc.removed.is_(None))
        if not admin:
            net_vpc_query.filter(NetVpc.tenant_id == g.tenant.get("tenant_id"))
        vpc = net_vpc_query.first()
        if vpc:
            error_msg = u"vpc_name重复了，请检查之后再试!"
            vpc_check = NetVpc.query.filter(NetVpc.id != args["vpc_id"],
                                            NetVpc.vpc_name.ilike("%\_{}".format(args["vpc_name"])),
                                            NetVpc.removed.is_(None)).first()
            if not vpc_check:
                error_msg = u""
                logic_pool_id, _ = split_vpc_name(vpc.vpc_name)
                vpc.vpc_name = combination_vpc_name(logic_pool_id=logic_pool_id, name=args["vpc_name"])
                if args["description"]:
                    vpc.description = args["description"]
                # fix bug:1498 by zhouming 201704017
                else:
                    vpc.description = ''
                db.session.commit()

        if error_msg:
            return error_msg
        return True

    @classmethod
    def get_vpc_by_id(cls, vpc_id):
        error_msg = u"vpc_id不存在或无权限操作!"
        admin, tenant_admin, user = False, False, False
        if int(g.user["is_super"]):
            admin = True
        # elif g.tenant["is_admin"]:
        #     tenant_admin = True
        # else:
        #     user = True
        net_vpc_query = NetVpc.query.filter(NetVpc.id == vpc_id, NetVpc.removed.is_(None))
        if not admin:
            net_vpc_query.filter(NetVpc.tenant_id == g.tenant.get("tenant_id"))
        vpc = net_vpc_query.first()
        if vpc:
            from app.utils.database import model_to_dict
            vpc = model_to_dict(vpc)
            vpc['client_pool_id'], vpc['vpc_name'] = split_vpc_name(vpc['vpc_name'])
            from app.management.logicpool.models import InfLogicPool
            client_pool = InfLogicPool.query.get(vpc['client_pool_id'])
            if not client_pool:
                error_msg = u"该租户无可用资源池"
                current_app.logger.error(u"调用用户平台，查询租户相关信息结束，{}！".format(error_msg))
                return False, error_msg
            vpc['client_pool_name'] = client_pool.name
            #######################################
            current_app.logger.info(u"调用用户平台，查询租户相关信息开始！")
            # 请求用户平台，获取租户信息
            from app.configs.api_uri import user as user_
            tenant_uri = user_.get_full_uri(user_.TENANT_URI)
            tenant_uri = r"{}/{}".format(tenant_uri, vpc['tenant_id'])
            status, data, content = g.request(uri=tenant_uri, method='GET')
            if status:
                current_app.logger.info(u"调用用户平台，查询租户相关信息结束，{}！".format(u"成功"))
            else:
                error_msg = data if data else u"不存在此租户，请联系管理员!"
                current_app.logger.error(u"调用用户平台，查询租户相关信息结束，{}！".format(error_msg))
            #######################################
            if status:
                # error_msg = u""
                vpc['tenant_name'] = data["name_zh"]
                # 查询关联子网列表详情
                from app.catalog.subnet.models import NetSubnet
                from app.catalog.subnet.constant import SubnetStatus
                subnets = NetSubnet.query.filter(NetSubnet.vpc_id == vpc_id,
                                                 NetSubnet.removed.is_(None),
                                                 NetSubnet.status.in_((SubnetStatus.normal.value,
                                                                       SubnetStatus.executing.value))).all()
                subnets = [model_to_dict(v) for v in subnets]
                data = {"vpc": vpc, "subnets": subnets}
                return True, data

        return False, error_msg

    @classmethod
    def delete_vpcs(cls, ids):
        vpcs = NetVpc.query.filter(NetVpc.id.in_(ids)).all()
        serial_numbers = []
        order_ids = []
        for vpc in vpcs:
            from app.management.logicpool.models import InfLogicPool
            from app.management.logicpool.models import InfPoolTenantRef
            from app.management.zone.models import InfZone
            logic_pool_id, _ = split_vpc_name(vpc.vpc_name)
            logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                 InfLogicPool.id == InfPoolTenantRef.pool_id) \
                .join(InfZone, InfZone.id == InfLogicPool.zone_id).add_columns(InfPoolTenantRef.project_id,
                                                                               InfZone.location).filter(
                InfLogicPool.id == logic_pool_id,
                InfLogicPool.removed.is_(None),
                InfPoolTenantRef.tenant_id == vpc.tenant_id).first()
            if logic_pool:
                logic_pool, project_id, location = logic_pool
                # logic_pool = model_to_dict(logic_pool)
                operation_object = g.user.get("name_zh")
                operation_name = "delete_vpcs"
                # 创建订单
                args = {"project_id": project_id, "location": location, "operation_object": operation_object,
                        "operation_name": operation_name, "vpc_id": vpc.id, "logic_pool_id": logic_pool_id,
                        "hypervisor_type": vpc.hypervisor_type}
                from app.order.constant import ResourceType
                order_d = {"user_id": g.user.get("current_user_id"), "tenant_id": g.tenant.get("tenant_id"),
                           "application_id": "", "application_name": "",
                           "resource_type": ResourceType.VPC.value, "operation_type": u"delete", "apply_info": args}
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
                error_msg = u"删除VPC失败!"
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
