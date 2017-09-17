# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-29
    vpc创建rest资源
"""
from flask import g, current_app
from flask_restful import Resource, reqparse

from app.catalog.vpc.constant import split_vpc_name, vpc_name_delimiter
from app.catalog.vpc.models import NetVpc
from app.catalog.vpc.services import VpcService
from app.configs.code import ResponseCode
from app.extensions import db
from app.utils.field_validations import vpc_hypervisor_type
from app.utils.helpers import format_date
from app.utils.my_logger import ActionType, ResourceType, log_decorator
from app.utils.parser import common_parser

# 参数解析对象生成
from app.utils.response import res_list_page, res

parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)


# 添加自定义参数


class Vpcs(Resource):
    """
        sxw 2016-12-29
        列出管理员下面的vpc列表
    """

    @staticmethod
    def post():
        parser_post = parser.copy()
        args = parser_post.parse_args()
        error_msg = u"对不起，您未登录!"
        if g.user and g.tenant:
            admin, tenant_admin, user = False, False, False
            if int(g.user["is_super"]):
                admin = True
            # elif g.tenant["is_admin"]:
            #     tenant_admin = True
            # else:
            #     user = True

            query = NetVpc.query.with_entities(NetVpc.id, NetVpc.tenant_id, NetVpc.vpc_name,
                                               NetVpc.hypervisor_type, NetVpc.is_default,
                                               NetVpc.created, NetVpc.description)
            if not admin:
                query = query.filter(NetVpc.tenant_id == g.tenant.get("tenant_id"))
            if args.get("q_type") == 'base':
                name = args["keyword"].get("name", "")
                # query = query.filter(db.or_(NetVpc.vpc_name.ilike("%{}%".format(name)),
                #                             NetVpc.tenant_id.ilike("%{}%".format(name)),
                #                             NetVpc.hypervisor_type.ilike("%{}%".format(name))))
                query = query.filter(NetVpc.vpc_name.ilike("%{}%{}%".format(vpc_name_delimiter(escape=True), name)))

            elif args.get("q_type") == 'advanced':
                keyword_d = args["keyword"]
                if keyword_d.get("vpc_name"):
                    query = query.filter(NetVpc.vpc_name.ilike("%\_%{}%".format(keyword_d["vpc_name"])))

                if keyword_d.get("tenant_id"):
                    query = query.filter(NetVpc.tenant_id.ilike("%{}%".format(keyword_d["tenant_id"])))

                if keyword_d.get("client_pool_id"):
                    query = query.filter(NetVpc.vpc_name.ilike("%{}%\_%".format(keyword_d["client_pool_id"])))

                if keyword_d.get("hypervisor_type"):
                    query = query.filter(NetVpc.hypervisor_type.ilike("%{}%".format(keyword_d["hypervisor_type"])))

                if keyword_d.get("is_default", None) in (0, 1):
                    query = query.filter(NetVpc.is_default == keyword_d["is_default"])

            query = query.filter(NetVpc.removed.is_(None), NetVpc.status.in_(('', 'executing'))). \
                order_by(NetVpc.id.desc())

            # query = NetVpc.query.options(load_only("id", "tenant_id", "vpc_name", "hypervisor_type")).\
            #                filter(NetVpc.vpc_name.ilike("%{}%".format(args["vpc_name"])),
            #                       NetVpc.tenant_id.ilike("%{}%".format(args["tenant_id"])),
            #                       NetVpc.hypervisor_type.ilike("%{}%".format(args["hypervisor_type"])))
            data = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False).items
            # data = [model_to_dict(v) for v in data]
            count = query.count()

            ids = []
            result = []
            client_pool_ids = []
            if admin:
                # 请求用户平台，获取租户列表
                from app.configs.api_uri import user as user_
                tenants_uri = user_.get_full_uri(user_.TENANT_LIST_NO_PAGE_URL)

                error_msg = u"租户列表请求失败，请联系运维人员！"
                status, tenants, content = g.request(uri=tenants_uri, method='POST', body={})
                if status:
                    tenant_id_name_d = {tenant['id']: tenant['name_zh'] for tenant in tenants}

                    # 取用户平台根据租户id，获取相应租户名字
                    for id_, tenant_id, vpc_name, hypervisor_type, is_default, created, description in data:
                        ids.append(id_)
                        # vpc_name 组合形式有logic_pool_id+_+vpc_name组成
                        client_pool_id, vpc_name = split_vpc_name(vpc_name)
                        tenant_name = tenant_id_name_d[int(tenant_id)]
                        client_pool_ids.append(int(client_pool_id))
                        result.append(
                            {"id": id_, "vpc_name": vpc_name, "tenant_id": tenant_id, "tenant_name": tenant_name,
                             "hypervisor_type": hypervisor_type, "client_pool_id": int(client_pool_id),
                             "is_default": is_default, "created": format_date(created, "%Y-%m-%d %H:%M:%S"),
                             "description": description})

                    # 根据客户资源池id，查询客户资源池名字
                    from app.management.logicpool.models import InfLogicPool
                    client_pools = InfLogicPool.query.filter(InfLogicPool.id.in_(client_pool_ids)).all()
                    for i, x in enumerate(client_pool_ids):
                        for client_pool in client_pools:
                            if int(client_pool.id) == x:
                                result[i].update({"client_pool_name": client_pool.name})
                                break
            else:
                for id_, tenant_id, vpc_name, hypervisor_type, is_default, created, description in data:
                    ids.append(id_)
                    client_pool_id, vpc_name = split_vpc_name(vpc_name)
                    client_pool_ids.append(int(client_pool_id))
                    result.append(
                        {"id": id_, "vpc_name": vpc_name, "tenant_id": tenant_id, "tenant_name": g.tenant.get("name_zh"),
                         "hypervisor_type": hypervisor_type, "is_default": is_default,
                         "client_pool_id": int(client_pool_id), "created": format_date(created, "%Y-%m-%d %H:%M:%S"),
                         "description": description})
                    # 根据客户资源池id，查询客户资源池名字
                    from app.management.logicpool.models import InfLogicPool
                    client_pools = InfLogicPool.query.filter(InfLogicPool.id.in_(client_pool_ids)).all()
                    for i, x in enumerate(client_pool_ids):
                        for client_pool in client_pools:
                            if int(client_pool.id) == x:
                                result[i].update({"client_pool_name": client_pool.name})
                                break

            return res_list_page(data=result, count=count, current_page=args["page"])

        return res(code=ResponseCode.ERROR, msg=error_msg)

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.vpc.value, id_name="ids")
    def delete(cls):
        parser_post = parser.copy()
        parser_post.add_argument("ids", required=True)
        args = parser_post.parse_args()
        try:
            ids = args["ids"].split(',')
        except (ValueError, TypeError) as e:
            error_msg = u"参数格式传递错误！"
            current_app.logger.warning("{}, exception:{}".format(error_msg, e))
        else:
            error_msg = u"对不起，您未登录!"
            if g.user and g.tenant:
                admin, tenant_admin, user = False, False, False
                if int(g.user["is_super"]):
                    admin = True
                # elif g.tenant["is_admin"]:
                #     tenant_admin = True
                # else:
                #     user = True

                error_msg = u"对不起，无权限操作"
                if admin:
                    error_msg = u"该vpc列表信息不存在或有部分不存在，ids={}!".format(ids)
                    id_length = len(ids)
                    # 针对只有1个元素值情况，避免in_报错
                    ids.append(None)
                    count = NetVpc.query.filter(NetVpc.id.in_(ids)).count()
                    if count == id_length:
                        error_msg = u"Vpc内还存在对应的子网或vlan信息，请先删除之后再试!"
                        from app.catalog.subnet.models import NetSubnet
                        from app.catalog.subnet.constant import SubnetStatus
                        subnets = NetSubnet.query.filter(NetSubnet.vpc_id.in_(ids),
                                                         NetSubnet.status.in_((SubnetStatus.normal.value,
                                                                               SubnetStatus.executing.value))).first()
                        if not subnets:
                            status, serial_number = VpcService.delete_vpcs(ids)
                            error_msg = serial_number
                            if status:
                                return res(data={"serial_number": serial_number})
        return res(ResponseCode.ERROR, msg=error_msg)


class CheckVpcName(Resource):
    """
        sxw 2017-1-4
        校验vpc_name是否重复
    """

    @staticmethod
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("vpc_name", required=True, trim=True)
        args = parser_post.parse_args()
        result = VpcService.check_vpc_name(args)
        if not result:
            return res()
        return res(ResponseCode.ERROR, msg=u'已经存在此vpc，请重新输入!')


class CreateVpc(Resource):
    """
        songxiaowei 2017-1-22

        管理员视图下创建vpc.
    """

    @classmethod
    @log_decorator(action=ActionType.create.value, resource=ResourceType.vpc.value)
    def post(cls):
        parser_post = parser.copy()
        parser_post.add_argument("vpc_name", required=True, trim=True)
        parser_post.add_argument("tenant_id", required=True, type=int)
        parser_post.add_argument("hypervisor_type", required=True, type=vpc_hypervisor_type, trim=True)
        parser_post.add_argument("client_pool_id", type=int, required=True, dest="logic_pool_id")
        parser_post.add_argument("description", trim=True, default="")
        args = parser_post.parse_args()
        error_msg = u"对不起，您未登录!"
        if g.user and g.tenant:
            admin, tenant_admin, user = False, False, False
            if int(g.user["is_super"]):
                admin = True
            # elif g.tenant["is_admin"]:
            #     tenant_admin = True
            # else:
            #     user = True
            error_msg = u"您无权操作!"
            if admin:
                status, serial_number = VpcService.create_vpc(args)
                error_msg = serial_number
                if status:
                    return res(data={"serial_number": serial_number})
        return res(ResponseCode.ERROR, msg=error_msg)


class Vpc(Resource):
    """
        sxw 2017-1-5

        管理员视图下相关vpc操作.
    """

    @classmethod
    @log_decorator(action=ActionType.delete.value, resource=ResourceType.vpc.value, id_name="vpc_id")
    def delete(cls, vpc_id):
        error_msg = u"对不起，您未登录!"
        if g.user and g.tenant:
            admin, tenant_admin, user = False, False, False
            if int(g.user["is_super"]):
                admin = True
            # elif g.tenant["is_admin"]:
            #     tenant_admin = True
            # else:
            #     user = True

            error_msg = u"对不起，无权限操作"
            if admin:
                error_msg = u"vpc_id不存在!"
                vpc = NetVpc.query.filter(NetVpc.id == vpc_id, NetVpc.removed.is_(None)).first()
                if vpc:
                    error_msg = u"Vpc内还存在对应的子网或vlan信息，请先删除之后再试!"
                    # 校验vpc内子网是否为空
                    from app.catalog.subnet.models import NetSubnet
                    from app.catalog.subnet.constant import SubnetStatus
                    subnet = NetSubnet.query.filter(NetSubnet.vpc_id == vpc_id,
                                                    NetSubnet.status.in_((SubnetStatus.normal.value,
                                                                          SubnetStatus.executing.value))).first()
                    if not subnet:
                        status, serial_number = VpcService.delete_vpcs([vpc.id])
                        error_msg = serial_number
                        if status:
                            return res(data={"serial_number": serial_number})
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    @log_decorator(action=ActionType.update.value, resource=ResourceType.vpc.value, id_name="vpc_id")
    def put(cls, vpc_id):
        parser_put = parser.copy()
        parser_put.add_argument("vpc_name", required=True, trim=True)
        # parser_put.add_argument("tenant_id", required=True, type=int)
        # parser_put.add_argument("hypervisor_type", required=True, type=vpc_hypervisor_type, trim=True)
        # parser_post.add_argument("client_pool_id", type=int, required=True, dest="logic_pool_id")
        parser_put.add_argument("description", trim=True, default="")
        args = parser_put.parse_args()
        error_msg = u"对不起，您未登录!"
        if g.user and g.tenant:
            args["vpc_id"] = vpc_id
            error_msg = VpcService.update_vpc(args)
            if error_msg is True:
                return res()
        return res(ResponseCode.ERROR, msg=error_msg)

    @classmethod
    def get(cls, vpc_id):
        error_msg = u"对不起，您未登录!"
        if g.user and g.tenant:
            # admin, tenant_admin, user = False, False, False
            # if int(g.user["is_super"]):
            #     admin = True
            # elif g.tenant["is_admin"]:
            #     tenant_admin = True
            # else:
            #     user = True
            status, data = VpcService.get_vpc_by_id(vpc_id)
            error_msg = data
            if status:
                return res(data=data)
        return res(ResponseCode.ERROR, msg=error_msg)


class TenantVpcSelect(Resource):
    """
        zhouming 2017-1-23

        租户视图下，列出资源池下创建vm或物理机可选的VPC列表
    """

    @staticmethod
    def post():
        parser_post = parser.copy()
        parser_post.add_argument("client_pool_id", type=int, required=True)
        args = parser_post.parse_args()
        # error_msg = u"对不起，您不是租户管理员，无权操作!"
        error_msg = u"对不起，用户获得租户信息失败，请重新登录!"
        if hasattr(g, "tenant") and g.tenant.get("tenant_id"):
            tenant_id = g.tenant.get("tenant_id")
            from app.management.logicpool.models import InfLogicPool
            client_pool_id = args['client_pool_id']
            client_pool = InfLogicPool.query.filter(InfLogicPool.id == client_pool_id,
                                                    InfLogicPool.removed.is_(None)).first()
            if client_pool is None:
                error_msg = u'对不起，所选客户资源池不存在！'
                return res(code=ResponseCode.ERROR, msg=error_msg)

            query = NetVpc.query.with_entities(NetVpc.id, NetVpc.tenant_id, NetVpc.vpc_name,
                                               NetVpc.hypervisor_type).filter()
            # _在mysql中是特殊字符
            name = str(client_pool_id) + vpc_name_delimiter(escape=True)
            data = query.filter(db.and_(NetVpc.vpc_name.ilike("{}%".format(name)),
                                        NetVpc.tenant_id == tenant_id,
                                        NetVpc.removed.is_(None),
                                        NetVpc.status.in_(('', 'executing')))).all()
            ids = []
            result = []
            for id_, tenant_id, vpc_name, hypervisor_type in data:
                ids.append(id_)
                client_pool_id, vpc_name = split_vpc_name(vpc_name)
                result.append(
                    {"id": id_, "vpc_name": vpc_name, "tenant_id": tenant_id, "hypervisor_type": hypervisor_type,
                     "client_pool_id": int(client_pool_id)})
            return res_list_page(data=result)

        return res(code=ResponseCode.ERROR, msg=error_msg)
