# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-12-23
    vpc相关模型.
"""
from sqlalchemy import text
from datetime import datetime

from app.catalog.subnet.constant import HypervisorType, IPSegmentStatus, IPFlag
from app.configs.default import DefaultConfig
from app.extensions import db
from app.utils.database import CRUDMixin


class CmdbIpSegment(db.Model, CRUDMixin):
    """
    sxw 2017-1-9

    CmdbIp子网模型
    """
    __tablename__ = 'cmdb_ip_segment'

    # id
    id = db.Column(db.Integer, primary_key=True)
    # 使用状态
    status = db.Column(db.Enum(*IPSegmentStatus.enums), nullable=False)
    # 网段ip
    segment = db.Column(db.String(15, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # 掩码
    mask = db.Column(db.String(15, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # 网关
    gateway = db.Column(db.String(15, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # dns
    dns = db.Column(db.String(15, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # 机房
    location = db.Column(db.String(100, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # vmware下为空
    vlan_id = db.Column(db.Integer)
    # 类型:'floating', 'vmware', 'openstack', 'loadbalance', 'internet', 'management', 'extnet'
    flag = db.Column(db.Enum(*IPFlag.enums), nullable=False)
    # 对应TITSM的ID
    coss_id = db.Column(db.String(40))

    @classmethod
    def get_free_subnet_ip_list(cls, segment_id):
        """
        zhouming 20161219
        获取子网可用地址空间
        """
        sql = u"""
                        select count(ip.id) from cmdb_ip as ip where ip.status=:statusfree
                        and ip.segment_id = :segment_id
                        and ip.id not in
                        (SELECT i.id FROM cmdb_ip as i, dis_resource_allocate as a
                        where FIND_IN_SET(i.id,a.allocated)
                        and i.segment_id=a.resource_id and i.segment_id = :segment_id and a.removed is Null)
                """
        result = db.session.execute(text(sql), {'statusfree': u'空闲', 'segment_id': segment_id}).scalar()
        return result

    @classmethod
    def get_segment_by_mask(cls, _mask):
        """
         zhouming 20161226
        通过地址空间获得可用的vmware网段
        :param _mask:
        :return:
        """
        sql = u"""
                    select se.* from cmdb_ip_segment as se where se.status=:statusfree
                    and se.mask = :mask and se.flag = :flag
                    and se.id not in
                    (SELECT i.id FROM cmdb_ip_segment as i, dis_resource_allocate as a
                    where FIND_IN_SET(i.id,a.allocated) and a.allocate_type= :allocate_type
                    and a.removed is Null)
                    ORDER BY se.id asc
                    LIMIT 1
                """
        status = u'空闲'
        flag = IPFlag.vmware.value
        allocate_type = 'NET_SEGMENT'
        result = db.session.execute(text(sql), {'statusfree': status, 'mask': _mask, 'flag': flag,
                                                'allocate_type': allocate_type})
        return result

    # @classmethod
    # def get_segment_by_mask(cls, _mask):
    #     """
    #      zhouming 20161226
    #     通过地址空间获得可用的vmware网段
    #     :param _mask:
    #     :return:
    #     """
    #     sql = u"""
    #                 SELECT i.*
    #                 FROM cmdb_ip_segment as i left join dis_resource_allocate as a
    #                 on ISNULL(a.removed) and a.allocate_type='NET_SEGMENT' and
    #                 (FIND_IN_SET(i.id,a.allocated) = 0 or FIND_IN_SET(i.id,a.allocated) is NULL)
    #                 where i.status='空闲'
    #                 and i.mask = :mask
    #                 and i.flag = :flag
    #                 and a.removed is Null
    #                 ORDER BY i.id asc
    #                 LIMIT 1
    #             """
    #     result = db.session.execute(text(sql), {'mask': _mask, 'flag': IPFlag.vmware.value})
    #     return result


class NetSubnet(db.Model, CRUDMixin):
    """
    sxw 2017-1-9

    VPC子网模型
    """
    __tablename__ = 'net_subnet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 子网名称
    name = db.Column(db.String(32, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # vpc表id
    vpc_id = db.Column(db.Integer, db.ForeignKey('net_vpc.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    # cmdb_ip_segment表id
    segment_id = db.Column(db.Integer, db.ForeignKey('cmdb_ip_segment.id', ondelete=u'CASCADE', onupdate=u'CASCADE'),
                           nullable=False)
    # 虚拟平台类型
    hypervisor_type = db.Column(db.Enum(*HypervisorType.enums), default=HypervisorType.openstack.value, nullable=False)
    # 对应openstack的uuid
    internal_uuid = db.Column(db.String(40, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), default='')
    # 描述
    description = db.Column(db.String(256, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    # 状态:'''',''expunge'', ''executing'', ''failed'',分别代表正常,回收站,执行中,执行失败.'
    status = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), default='')
    # 创建时间
    created = db.Column(db.DateTime, default=datetime.now())
    # 删除时间
    removed = db.Column(db.DateTime)

    # vpc实体
    vpc = db.relationship(u'NetVpc')
    # 网段实体
    segment = db.relationship(u'CmdbIpSegment')


