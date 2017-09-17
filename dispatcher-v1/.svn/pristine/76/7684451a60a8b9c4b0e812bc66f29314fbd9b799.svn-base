# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-29

    subnet创建rest资源
"""
from flask import current_app
from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import func

from app.catalog.subnet.models import NetSubnet, CmdbIpSegment
from app.catalog.subnet.services import SubnetService
from app.cmdb.subnet.models import CmdbIp
from app.configs.code import ResponseCode
from app.extensions import db
from app.utils.field_validations import subnet_os_segment, subnet_gateway
from app.utils.parser import common_parser

# 参数解析对象生成
from app.utils.response import res, res_details, res_list_page
# 将请求写入日志
from app.utils.my_logger import ActionType, ResourceType, log_decorator

parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


# 添加自定义参数
class TenantCreateSubnet(Resource):
    """
        songxiaowei 2017-1-22

        租户视图下，subnet的基础操作之创建，默认针对''openstack''
    """

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.subnet.value)
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("vpc_id", type=int, required=True)
        parser_post.add_argument("name", required=True, trim=True)
        parser_post.add_argument("segment", type=subnet_os_segment, required=True, trim=True)
        parser_post.add_argument("gateway", required=True, type=subnet_gateway, trim=True)
        parser_post.add_argument("description", trim=True, default="")
        args = parser_post.parse_args()
        # 此接口针对openstack，因此添加hypervisor_type
        status, serial_number = SubnetService.create_os_subnet(args)
        if status:
            return res(data={"serial_number": serial_number}, msg=u"请查看订单")
        return res(ResponseCode.ERROR, msg=serial_number)


class TenantSubnet(Resource):
    """
        sxw 2017-1-12

        租户视图下，subnet的基础操作，默认针对''openstack''
    """

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.subnet.value, id_name="subnet_id")
    def delete(cls, subnet_id):
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            error_msg = u"内含主机，不能删除此子网!"
            from app.configs.api_uri import network as network_
            subnet_check_uri = network_.get_full_uri(network_.SUBNET_IS_USED)
            subnet_check_d = {"subnet_id": subnet.id}
            if subnet.hypervisor_type == 'openstack':
                from app.management.logicpool.models import InfLogicPool
                from app.management.logicpool.models import InfPoolTenantRef
                logic_pool_id = subnet.vpc.vpc_name.split('_')[0]
                vpc_tenant_id = subnet.vpc.tenant_id
                logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                     InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
                    InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                        InfLogicPool.removed.is_(None),
                                                        InfPoolTenantRef.tenant_id == vpc_tenant_id).first()
                logic_pool, project_id = logic_pool
                subnet_check_d.update({"project_id": project_id, "logic_pool_id": logic_pool.id})
            status, data, content = g.request(uri=subnet_check_uri, method='POST', body=subnet_check_d)
            if not status:
                error_msg = data if data else error_msg
                current_app.logger.error(
                    "调用子网检查是否被占用接口失败，uri={}, body={}, 错误消息为:{}!".format(subnet_check_uri, subnet_check_d, error_msg))
            # 此处根据调用net接口值返回成功则置状态为expunge
            if status:
                subnet.status = "expunge"
                db.session.commit()
                return res()
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.subnet.value, id_name="subnet_id")
    def put(cls, subnet_id):
        parser_put = parser.copy()
        parser_put.add_argument("name", required=True, trim=True)
        parser_put.add_argument("description", trim=True, default="")
        args = parser_put.parse_args()
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            if args["name"]:
                subnet.name = args["name"]

            if args["description"]:
                subnet.description = args["description"]
            # fix bug:1499 by zhouming 201704017
            else:
                subnet.description = ''
            db.session.commit()
            return res()
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    def get(cls, subnet_id):
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            from app.utils.database import model_to_dict
            from IPy import IP
            capacity = IP('{}/{}'.format(subnet.segment.segment, subnet.segment.mask)).len()
            subnet = model_to_dict(subnet)
            # 网段容量
            subnet["segment"]["capacity"] = CmdbIpSegment.get_free_subnet_ip_list(subnet["segment"]["id"])
            # vpc名字过滤
            from app.catalog.vpc.constant import split_vpc_name
            _, vpc_name = split_vpc_name(subnet["vpc"]["vpc_name"])
            subnet["vpc"]["vpc_name"] = vpc_name
            return res_details(data=subnet)
        return res(ResponseCode.ERROR, msg=error_msg)


class TenantSubnets(Resource):
    """
        sxw 2017-2-8

        租户视图下，subnets的基础操作，默认针对''openstack''
    """

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.subnet.value, id_name="ids")
    def delete(cls):
        parser_delete = parser.copy()
        parser_delete.add_argument("ids", required=True)
        args = parser_delete.parse_args()
        try:
            ids = args["ids"].split(',')
        except (ValueError, TypeError) as e:
            error_msg = u"参数格式传递错误！"
            current_app.logger.warning("{}, exception:{}".format(error_msg, e))
        else:
            error_msg = u"该子网信息不存在或有部分不存在，ids={}!".format(ids)
            id_length = len(ids)
            # 针对只有1个元素值情况，避免in_报错
            ids.append(None)
            subnets = NetSubnet.query.filter(NetSubnet.id.in_(ids)).all()
            if len(subnets) == id_length:
                for subnet in subnets:
                    error_msg = u"内含主机，不能删除此子网, id={}!".format(subnet.id)
                    from app.configs.api_uri import network as network_
                    subnet_check_uri = network_.get_full_uri(network_.SUBNET_IS_USED)
                    subnet_check_d = {"subnet_id": subnet.id}
                    if subnet.hypervisor_type in ('openstack', u'openstack'):
                        from app.management.logicpool.models import InfLogicPool
                        from app.management.logicpool.models import InfPoolTenantRef
                        logic_pool_id = subnet.vpc.vpc_name.split('_')[0]
                        vpc_tenant_id = subnet.vpc.tenant_id
                        logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                             InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
                            InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                                InfLogicPool.removed.is_(None),
                                                                InfPoolTenantRef.tenant_id == vpc_tenant_id).first()
                        logic_pool, project_id = logic_pool
                        subnet_check_d.update({"project_id": project_id, "logic_pool_id": logic_pool.id})
                    status, data, content = g.request(uri=subnet_check_uri, method='POST', body=subnet_check_d)
                    if not status:
                        error_msg = data if data else error_msg
                        current_app.logger.error(
                            "调用子网检查是否被占用接口失败，uri={}, body={}, 错误消息为:{}!".format(subnet_check_uri, subnet_check_d,
                                                                                error_msg))
                        break

                # 此处根据调用net接口值返回成功则置状态为expunge
                if status:
                    NetSubnet.query.filter(NetSubnet.id.in_(ids)).update({NetSubnet.status: "expunge"},
                                                                         synchronize_session=False)
                    db.session.commit()
                    return res()
        return res(ResponseCode.ERROR, msg=error_msg)


class TenantVmwareSubnet(Resource):
    """
        songxiaowei 2017-1-22

        租户视图下，subnet的基础操作，新增vmware vpc子网
    """

    @staticmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.subnet.value)
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("vpc_id", type=int, required=True)
        parser_post.add_argument("name", required=True, trim=True)
        parser_post.add_argument("segment_id", type=int, required=True, trim=True)
        parser_post.add_argument("description", trim=True, default="")
        args = parser_post.parse_args()
        # 此接口针对vmware，因此添加hypervisor_type
        status, serial_number = SubnetService.create_vm_subnet(args)
        if status:
            return res(data={"serial_number": serial_number}, msg=u"请查看订单")
        return res(ResponseCode.ERROR, msg=serial_number)


class TenantSubnetList(Resource):
    """
        songxiaowei 2017-1-22
        
        租户视图下，列出全部可用子网信息
    """

    @classmethod
    def post(cls):
        from app.catalog.vpc.models import NetVpc
        subnets = NetSubnet.query.join(NetVpc, NetSubnet.vpc_id == NetVpc.id).filter(
            NetVpc.tenant_id == g.tenant.get("tenant_id"),
            NetSubnet.removed.is_(None),
            NetSubnet.status.in_(("", "executing"))).all()

        from app.utils.database import model_to_dict
        print ("subnet list m2d", model_to_dict(subnets))
        data = model_to_dict(subnets)

        # 添加子网网段容量
        result = []
        name_format = u"{name}(子网容量：{capacity})"
        for id_, name, vpc_id, segment_id, segment, mask, gateway in data:
            capacity = CmdbIpSegment.get_free_subnet_ip_list(segment_id)
            result.append(
                {"id": id_, "name": name_format.format(name=name, capacity=capacity), "segment": segment, "mask": mask,
                 "gateway": gateway, "capacity": capacity})

        return res(data=subnets)


class UserSubnet(Resource):
    """
        songxiaowei 2017-1-22

        租户视图下，subnet的基础操作，新增vmware vpc子网
    """

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.subnet.value, id_name="subnet_id")
    def delete(cls, subnet_id):
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            error_msg = u"释放子网资源，需要子网内部为空!"
            from app.configs.api_uri import network as network_
            subnet_check_uri = network_.get_full_uri(network_.SUBNET_IS_USED)
            subnet_check_d = {"subnet_id": subnet.id}
            if subnet.status == 'openstack':
                from app.management.logicpool.models import InfLogicPool
                from app.management.logicpool.models import InfPoolTenantRef
                logic_pool_id = subnet.vpc.vpc_name.split('_')[0]
                vpc_tenant_id = subnet.vpc.tenant_id
                logic_pool = InfLogicPool.query.join(InfPoolTenantRef,
                                                     InfLogicPool.id == InfPoolTenantRef.pool_id).add_columns(
                    InfPoolTenantRef.project_id).filter(InfLogicPool.id == logic_pool_id,
                                                        InfLogicPool.removed.is_(None),
                                                        InfPoolTenantRef.tenant_id == vpc_tenant_id).first()
                logic_pool, project_id = logic_pool
                subnet_check_d.update({"project_id": project_id, "logic_pool_id": logic_pool.id})
            status, data, content = g.request(uri=subnet_check_uri, method='POST', body=subnet_check_d)
            if not status:
                error_msg = data if data else error_msg
                current_app.logger.error(
                    "调用子网检查是否被占用接口失败，uri={}, body={}, 错误消息为:{}!".format(subnet_check_uri, subnet_check_d, error_msg))
            # 此处根据调用net接口值返回成功则置状态为expunge
            if status:
                subnet.status = "expunge"
                db.session.commit()
                return res()
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.subnet.value, id_name="subnet_id")
    def put(cls, subnet_id):
        parser_put = parser.copy()
        parser_put.add_argument("name", trim=True)
        parser_put.add_argument("description", trim=True)
        args = parser_put.parse_args()
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            if args["name"]:
                subnet.name = args["name"]

            if args["description"]:
                subnet.description = args["description"]
            # fix bug:1499 by zhouming 201704017
            else:
                subnet.description = ''
            db.session.commit()
            return res()
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    def get(cls, subnet_id):
        error_msg = u"该子网信息不存在id={}不存在!".format(subnet_id)
        subnet = NetSubnet.query.get(subnet_id)
        if subnet:
            from app.utils.database import model_to_dict
            from IPy import IP
            capacity = IP('{}/{}'.format(subnet.segment.segment, subnet.segment.mask)).len()
            subnet = model_to_dict(subnet)
            # 网段容量减去广播地址、0、网关地址254
            subnet["segment"]["capacity"] = CmdbIpSegment.get_free_subnet_ip_list(subnet["segment"]["id"])
            # vpc名字过滤
            from app.catalog.vpc.constant import split_vpc_name
            _, vpc_name = split_vpc_name(subnet["vpc"]["vpc_name"])
            subnet["vpc"]["vpc_name"] = vpc_name
            return res_details(data=subnet)
        return res(ResponseCode.ERROR, msg=error_msg)


class CheckSubnetName(Resource):
    """
        songxiaowei 2017-1-22

        校验当前租户下，vpc名称是否租户内唯一
    """

    @classmethod
    def post(cls):
        parser_post = parser.copy()
        parser_post.add_argument("name", required=True, trim=True)
        args = parser_post.parse_args()
        from app.catalog.vpc.models import NetVpc
        subnet = NetSubnet.query.join(NetVpc, NetSubnet.vpc_id == NetVpc.id).filter(
            NetVpc.tenant_id == g.tenant.get("tenant_id"), NetSubnet.name == args["name"],
            NetSubnet.removed.is_(None)).first()
        if not subnet:
            return res()
        return res(ResponseCode.ERROR, msg=u"租户内子网名字唯一，请更新后再试!")


class TenantVpcSubnetSelect(Resource):
    """
        zhouming 2017-1-23
        suyn 2017-4-10 计算子网容量，并标注在子网名称之后，如：subnet_name(子网容量：16)

        租户视图下，列出资源池下创建vm或物理机可选的子网列表
    """

    @classmethod
    def post(cls, vpc_id):
        from app.catalog.vpc.models import NetVpc
        query = NetSubnet.query.join(NetVpc, NetVpc.id == NetSubnet.vpc_id) \
            .join(CmdbIpSegment, NetSubnet.segment_id == CmdbIpSegment.id) \
            .with_entities(NetSubnet.id, NetSubnet.name, NetSubnet.vpc_id, NetSubnet.segment_id, CmdbIpSegment.segment,
                           CmdbIpSegment.mask, CmdbIpSegment.gateway).filter()
        subnets = query.filter(
            NetVpc.tenant_id == g.tenant.get("tenant_id"),
            NetSubnet.vpc_id == vpc_id,
            NetSubnet.removed.is_(None),
            NetSubnet.status.in_(("", "executing"))).all()

        #suyn 2017-4-10 添加子网网段容量
        result = []
        name_format = u"{name}(子网容量：{capacity})"
        if subnets:
            for subnet in subnets:
                capacity = CmdbIpSegment.get_free_subnet_ip_list(subnet.segment_id)
                result.append(
                    {"id": subnet.id, "name": name_format.format(name=subnet.name, capacity=capacity), "segment": subnet.segment,
                     "mask": subnet.mask, "gateway": subnet.gateway, "capacity": capacity})

        return res(data=result)


class TenantVpcSubnetList(Resource):
    """
        zhouming 2017-1-23
        suyn 2017-4-10 show subnet when its capacity is 0

        租户视图下，列出资源池下VPC的子网列表
    """

    @classmethod
    def post(cls, vpc_id):
        parser_get = parser.copy()
        parser_get.add_argument("vpc_name", trim=True, default="")
        args = parser_get.parse_args()
        error_msg = u"对不起，用户获得租户信息失败，请重新登录!"
        if hasattr(g, "tenant") and g.tenant and g.tenant.get("tenant_id"):
            query = NetSubnet.query.join(CmdbIpSegment, NetSubnet.segment_id == CmdbIpSegment.id) \
                .with_entities(NetSubnet.id, NetSubnet.name, NetSubnet.hypervisor_type,
                               NetSubnet.segment_id, CmdbIpSegment.segment, CmdbIpSegment.mask,
                               CmdbIpSegment.gateway, NetSubnet.description).filter(NetSubnet.vpc_id == vpc_id)

            # query = NetSubnet.query.join(CmdbIpSegment, NetSubnet.segment_id == CmdbIpSegment.id) \
            #     .outerjoin(CmdbIp, CmdbIp.segment_id == NetSubnet.segment_id) \
            #     .with_entities(NetSubnet.id, NetSubnet.name, NetSubnet.hypervisor_type,
            #                    NetSubnet.segment_id, CmdbIpSegment.segment, CmdbIpSegment.mask,
            #                    CmdbIpSegment.gateway, NetSubnet.description,
            #                    func.count(CmdbIp.id)).filter(NetSubnet.vpc_id == vpc_id,
            #                                                  CmdbIp.status == u"空闲")

            if args.get("q_type") == 'base':
                name = args["keyword"].get("name", "")
                if name:
                    # query = query.filter(db.or_(NetSubnet.name.ilike("%{}%".format(name)),
                    #                             CmdbIpSegment.segment.ilike("%{}%".format(name)),
                    #                             CmdbIpSegment.gateway.ilike("%{}%".format(name))))
                    query = query.filter(NetSubnet.name.ilike("%{}%".format(name)))
            elif args.get("q_type") == 'advanced':
                keyword_d = args["keyword"]
                if keyword_d.get("name"):
                    query = query.filter(NetSubnet.name.ilike("%{}%".format(keyword_d["name"])))

                if keyword_d.get("segment"):
                    query = query.filter(CmdbIpSegment.segment.ilike("%{}%".format(keyword_d["segment"])))

                if keyword_d.get("gateway"):
                    query = query.filter(CmdbIpSegment.gateway.ilike("%{}%".format(keyword_d["gateway"])))

            from app.catalog.subnet.constant import SubnetStatus
            query = query.filter(NetSubnet.removed.is_(None),
                                 NetSubnet.status.in_(
                                     (SubnetStatus.normal.value, SubnetStatus.executing.value))).group_by(NetSubnet.id)
            data = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False).items
            count = query.count()

            # 添加子网网段容量
            result = []
            for id_, name, hypervisor_type, segment_id, segment, mask, gateway, description in data:
                capacity = CmdbIpSegment.get_free_subnet_ip_list(segment_id)
                result.append(
                    {"id": id_, "name": name, "segment": segment, "mask": mask, "gateway": gateway,
                     "capacity": capacity, "description": description})

            return res_list_page(data=result, count=count, current_page=args["page"])

        return res(code=ResponseCode.ERROR, msg=error_msg)


class ChoseIpSegment(Resource):
    """
        songxiaowei 2017-2-8

        根据网段位数，随机分配网段
    """

    @staticmethod
    def post():
        """通过子网位数选择segment"""
        parser_post = parser.copy()
        # 掩码(地址空间）
        parser_post.add_argument("mask", type=int, choices=(24, 25, 26, 27, 28), required=True)
        args = parser_post.parse_args()
        return SubnetService.get_segment_by_mask(args)


class CheckName(Resource):
    """
        songxiaowei 2017-2-9

        检查在同一vpc下是否已有此子网名称
    """

    @classmethod
    def post(cls, vpc_id):
        parser_post = parser.copy()
        parser_post.add_argument("name", required=True, trim=True)
        args = parser_post.parse_args()
        error_msg = u"此名字为空！"
        if args["name"]:
            error_msg = u"此vpc_id无效，id={}!".format(vpc_id)
            from app.catalog.vpc.models import NetVpc
            vpc = NetVpc.query.get(vpc_id)
            if vpc:
                error_msg = u"该vpc下，已经存在此名字，请重试!"
                subnet = NetSubnet.query.filter(NetSubnet.removed.is_(None), NetSubnet.vpc_id == vpc.id,
                                                NetSubnet.name == args["name"]).first()
                if not subnet:
                    return res()

        return res(ResponseCode.ERROR, msg=error_msg)


class CheckSegment(Resource):
    """
        songxiaowei 2017-2-9

        检查在同一vpc下是否已有此网段信息
    """

    @classmethod
    def post(cls, vpc_id):
        parser_post = parser.copy()
        parser_post.add_argument("segment", type=subnet_os_segment, required=True, trim=True)
        args = parser_post.parse_args()
        error_msg = u"此vpc_id无效，id={}!".format(vpc_id)
        from app.catalog.vpc.models import NetVpc
        vpc = NetVpc.query.get(vpc_id)
        if vpc:
            error_msg = u"该vpc下，已经存在此网段信息，请重试!"
            import IPy
            segment = IPy.IP(args["segment"])
            subnet = NetSubnet.query.join(CmdbIpSegment, CmdbIpSegment.id == NetSubnet.segment_id).filter(
                NetSubnet.removed.is_(None), NetSubnet.vpc_id == vpc.id,
                                             CmdbIpSegment.segment == segment.net().strFullsize(),
                                             CmdbIpSegment.mask == segment.netmask().strFullsize()).first()
            if not subnet:
                return res()

        return res(ResponseCode.ERROR, msg=error_msg)


class RecycleSubnets(Resource):
    """
        songxiaowei 2017-2-16

        回收站的子网操作
    """

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.subnet.value, id_name="ids")
    def delete(cls):
        parser_delete = parser.copy()
        parser_delete.add_argument("ids", required=True)
        args = parser_delete.parse_args()
        try:
            ids = args["ids"].split(',')
        except (ValueError, TypeError) as e:
            error_msg = u"参数格式传递错误！"
            current_app.logger.warning("{}, exception:{}".format(error_msg, e))
        else:
            ids.append(None)
            subnets = NetSubnet.query.filter(NetSubnet.id.in_(ids), NetSubnet.status == u"expunge").all()
            status, serial_number = SubnetService.delete_subnets(subnets)
            if status:
                NetSubnet.query.filter(NetSubnet.id.in_(ids)).update({NetSubnet.status: "deleting"},
                                                                     synchronize_session=False)
                return res(data={"serial_number": serial_number})
            error_msg = serial_number
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.subnet.value, id_name="ids")
    def put(cls):
        parser_put = parser.copy()
        parser_put.add_argument("ids", required=True)
        args = parser_put.parse_args()
        try:
            ids = args["ids"].split(',')
        except (ValueError, TypeError) as e:
            error_msg = u"参数格式传递错误！"
            current_app.logger.warning("{}, exception:{}".format(error_msg, e))
        else:
            error_msg = u"该子网信息不存在或有部分不存在，ids={}!".format(ids)
            id_length = len(ids)
            # 针对只有1个元素值情况，避免in_报错
            ids.append(None)
            subnets = NetSubnet.query.filter(NetSubnet.id.in_(ids), NetSubnet.status == "expunge").all()
            if len(subnets) == id_length:
                # 将状态改为可用
                NetSubnet.query.filter(NetSubnet.id.in_(ids)).update({NetSubnet.status: ""},
                                                                     synchronize_session=False)
                db.session.commit()
                return res()
        return res(ResponseCode.ERROR, msg=error_msg)
