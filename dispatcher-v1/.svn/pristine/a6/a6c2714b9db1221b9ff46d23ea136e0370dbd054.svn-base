# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-23
    vpc相关模型.
"""
from sqlalchemy import text

from app.catalog.vpc.constant import vpc_name_delimiter
from app.extensions import db
from app.utils.database import CRUDMixin


class NetVpc(db.Model, CRUDMixin):
    """VPC实体模型."""
    __tablename__ = 'net_vpc'

    # 编号,自增
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 租户对应的id
    tenant_id = db.Column(db.Integer, nullable=False)
    # vpc的名称
    vpc_name = db.Column(db.String(32), nullable=False)
    # 虚拟化平台的类型，值可以为“openstack”或“vmware”
    hypervisor_type = db.Column(db.String(10), nullable=False)
    # 如果hypervisor为”openstack“，该值对应为openstack内部的network对象的uuid；vmware平台下该值可以为空
    internal_uuid = db.Column(db.String(40))
    # '如果hypervisor为”openstack“，该值对应为openstack内部的network对象关联的的router的id，vmware平台下该值可以为空'
    router_uuid = db.Column(db.String(40))
    # 创建时间
    created = db.Column(db.DateTime, nullable=False)
    # 删除时间
    removed = db.Column(db.DateTime)
    # 状态:'','expunge', 'executing', 'failed',分别代表正常,回收站, 执行中, 执行失败.
    status = db.Column(db.String(15))
    # vpc标识，1为默认；0为手动
    is_default = db.Column(db.Integer, server_default="0")
    # 描述
    description = db.Column(db.String(256))

    @classmethod
    def check_vpc_name(cls, vpc_name):
        u"""
            sxw 2017-1-4
            查询数据库中是否存在此net_vpc
        """
        vpc_name = '%' + vpc_name_delimiter(escape=True) + vpc_name
        sql = u"""
                 select id from net_vpc where vpc_name like :vpc_name and ISNULL(`removed`)
               """
        return db.session.execute(text(sql), {"vpc_name": vpc_name})
