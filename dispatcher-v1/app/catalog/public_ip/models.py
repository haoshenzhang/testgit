# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
公网IP  model层
wei lai 2016/12/16
"""

import datetime
from sqlalchemy import text

from app.catalog.public_ip.constant import IpStatus, BoundObjectType, NatType
from app.extensions import db
from app.order.constant import ResourceType
from app.utils.database import CRUDMixin


class CmdbInternetIp(db.Model, CRUDMixin):
    """
    公网IP 数据基础表
    """
    __tablename__ = 'cmdb_internet_ip'

    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(15, u'utf8_unicode_ci'), nullable=False, unique=True)
    segment_id = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Enum(u'使用中', u'预分配', u'注销', u'空闲', u'删除', u'预留'), nullable=False)
    usage = db.Column(db.Enum(u'生产', u'预投产', u'测试', u'UAT', u'办公'))
    network = db.Column(db.Enum(u'内网', u'内网DMZ', u'InternetDMZ', u'企业互联DMZ', u'测试', u'大数据', u'管理', u'其他', u'办公网段'))
    app_net = db.Column(db.Enum(u'传统业务系统', u'新一代共享系统', u'新一代CA专属系统', u'新一代MU专属系统', u'新一代CZ专属系统', u'新一代其它专属系统', u'无限制'))
    app_level = db.Column(db.Enum(u'高等级', u'差异化', u'无限制'))
    app_category = db.Column(db.Enum(u'WEB', u'APP', u'DB', u'无限制', u'APP_DB', u'LB'))
    type = db.Column(db.Enum(u'物理机IP', u'虚拟机IP', u'服务IP', u'NASIP', u'设备管理IP', u'监控管理IP', u'负载均衡', u'SCAN IP', u'应用IP'))
    location = db.Column(db.Enum(u'东四', u'三里屯', u'国富瑞'))
    _class = db.Column('class', db.Enum(u'HOSTIP', u'NASIP', u'负载均衡IP'))

    @classmethod
    def update_ip_status(cls, id_, status):
        """
        修改公网IP的状态  预分配 ，根据公网IP的id
        :param id_: 公网IP的ID
        :return:
        """
        sql_update = u"""update cmdb_internet_ip set `status` = :status where id = :id_
                    """
        db.session.execute(text(sql_update), {'id_': id_, 'status': status})

    @classmethod
    def update_vpc_ip_status(cls, id_):
        """
        创建vpc，更改占用的ip（cmdb_ip表）
        :param id_: 公网IP的ID
        :return:
        """
        status = IpStatus.using
        sql_update = u"""update cmdb_ip set `status` = :status where id = :id_
                        """
        db.session.execute(text(sql_update), {'id_': id_, 'status': status})

    @classmethod
    def get_num_free_int_ip(cls, location):
        """
        wei lai 20161227 获取指定数量的空闲公网IP并不在记账表中

        :param location: 位置
        :return:
        """
        sql = u"""
                   select ip.id as id, ip.addr as internet_ip,ip.segment_id as segment_id from cmdb_internet_ip as ip where ip.status = :status
                       and ip.location = :location
                       and ip.id not in
                       (SELECT i.id FROM cmdb_internet_ip as i, dis_resource_allocate as a
                       where FIND_IN_SET(i.id,a.allocated) and a.allocate_type= 'INTERNET_IP'
                       and i.segment_id=a.resource_id and a.removed is Null)
                       ORDER BY ip.id asc
               """
        result = db.session.execute(text(sql), {'status': IpStatus.free, 'location': location})
        return result


class DisResourceAllocate(db.Model, CRUDMixin):
    """
    资源记账表
    """
    __tablename__ = 'dis_resource_allocate'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    allocate_type = db.Column(db.String(20), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)
    allocated = db.Column(db.String(100), nullable=False, server_default=text("'0'"))
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def update_allocate_removed(cls, order_id, allocate_type):
        """
        删除记账表中的数据
        :param order_id: 订单ID
        :param allocate_type: 记账类型
        :return:
        """
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_update = u"""update dis_resource_allocate set `removed` = :removed where order_id = :order_id
                    and allocate_type = :allocate_type
                            """
        db.session.execute(text(sql_update), {'removed': removed, 'order_id': order_id, 'allocate_type': allocate_type})


class MappingResTenantRef(db.Model, CRUDMixin):
    """
    公网IP与租户间的关系表
    """
    __tablename__ = 'mapping_res_tenant_ref'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, nullable=False)
    resource_type = db.Column(db.String(20), nullable=False)
    resource_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def create_ip_tenant_ref(cls, tenant_id, resource_id):
        """
        公网IP与租户进行绑定
        :param tenant_id: 租户ID
        :param resource_id: 公网IP ID
        :return:
        """
        resource_type = ResourceType.PUBLIC_IP.value
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_insert = u"""insert into mapping_res_tenant_ref (`tenant_id`, `resource_id`, `resource_type`, `created`)
                          VALUE (:tenant_id, :resource_id, :resource_type, :created)"""
        db.session.execute(text(sql_insert), {'tenant_id': tenant_id, 'resource_id': resource_id,
                                              'resource_type': resource_type, 'created': created})

    @classmethod
    def get_ipcount_by_tenant(cls, tenant_id):
        """
        wei lai
        通过租户ID查询租户下的总公网ip
        :param tenant_id:
        :return:
        """
        resource_type = ResourceType.PUBLIC_IP.value
        sql = u"""select count(*) from mapping_res_tenant_ref rtr where rtr.tenant_id = :tenant_id AND
               rtr.removed is null and  rtr.resource_type = :resource_type"""
        data = db.session.execute(text(sql),{'tenant_id': tenant_id, 'resource_type': resource_type})
        return data

    @classmethod
    def get_used_ipcount_by_tenant(cls, tenant_id):
        """
        wei lai
        通过租户ID查询已使用的公网ip数量
        :param tenant_id:
        :return:
        """
        resource_type = ResourceType.PUBLIC_IP.value
        status = IpStatus.using
        sql = u"""select count(*) from mapping_res_tenant_ref a,cmdb_internet_ip b where a.tenant_id = :tenant_id
                  and a.resource_id = b.id and a.resource_type= :resource_type  and b.`status`= :status and a.removed is null """
        data = db.session.execute(text(sql), {'tenant_id': tenant_id, 'status': status, 'resource_type': resource_type})
        return data


class NetVpn(CRUDMixin):

    @classmethod
    def check_tenant_vpn(cls, tenant_id):
        """
        wei lai
        通过租户ID查询VPN
        :param tenant_id:
        :return:
        """
        sql = u"""select * from net_vpn a where a.tenant_id = :tenant_id and a.removed is null and status is null"""
        data = db.session.execute(text(sql), {'tenant_id': tenant_id})
        return data


class NetInternetIp(CRUDMixin):

    @classmethod
    def get_public_ip_tenant(cls, tenant_id):
        """
        查询租户下的公网ip地址及状态（未删除，未进回收站的，正在执行中的）
        :param tenant_id:
        :return:
        """
        resource_type = ResourceType.PUBLIC_IP.value
        sql = u"""select * from mapping_res_tenant_ref a left join cmdb_internet_ip c on a.resource_id = c.id
                where a.`status` is null and a.tenant_id =:tenant_id
                 and a.resource_type = :resource_type and a.removed is null and a.resource_id
                 not in(select n.target_id from net_internet_ip n where `status` is not null and removed is null)

        """
        data = db.session.execute(text(sql), {'tenant_id': tenant_id, 'resource_type': resource_type})
        return data

    @classmethod
    def get_public_ip_id(cls, target_id):
        """
        租户绑定的公网ip_id查询net_internet_ip表中的信息
        :param target_id: 对应的cmdb_ip表中id
        :return:
        """
        status = IpStatus.expunge
        sql = u"""select * from net_internet_ip a where a.target_id = :target_id
                and  a.`status` is null and a.removed is null
                """
        data = db.session.execute(text(sql), {'target_id': target_id, 'status': status})
        return data

    @classmethod
    def get_lb_vip(cls, source_ip_id):
        """
        根据内网ip查询负载均衡的名称
        :param source_ip_id:
        :return:
        """
        status = IpStatus.expunge
        sql = u"""select a.name from net_f5_lbpolicy a  where a.vip_id = :source_ip_id
                  and  a.removed is null
              """
        data = db.session.execute(text(sql), {'source_ip_id': source_ip_id, 'status': status})
        return data

    @classmethod
    def get_vm_ip(cls, source_ip_id):
        """
        根据内网ip查询虚机物理机的名称
        :param source_ip_id:
        :return:
        """
        status = IpStatus.expunge
        sql = u"""select b.name from mapping_host_ip_ref a , cmdb_host_logicserver b
                    where a.host_id = b.id and a.ip_id=:source_ip_id and b.removed is null
              """
        data = db.session.execute(text(sql), {'source_ip_id': source_ip_id, 'status': status})
        return data

    @classmethod
    def get_cmdb_by_id(cls, target_id):
        """
        查询cmdb表中ip的信息通过id
        :param target_id:
        :return:
        """
        sql = u"""select * from  cmdb_internet_ip a where a.id =:target_id
                """
        data = db.session.execute(text(sql), {'target_id': target_id})
        return data

    @classmethod
    def delete_ip(cls, target_id, tenant_id):
        """
        公网ip进回收站
        :param target_id:
        :param tenant_id:
        :return:
        """
        status = IpStatus.expunge
        sql = u"""update mapping_res_tenant_ref a set a.`status` = :status  where a.resource_id =:target_id
                  and a.tenant_id = :tenant_id
                    """
        db.session.execute(text(sql), {'target_id': target_id, 'status': status, 'tenant_id': tenant_id})

    @classmethod
    def restore_public_ip(cls, target_id,  tenant_id):
        """
        公网ip还原
        :param target_id:
        :param tenant_id:
        :return:
        """
        status = IpStatus.expunge
        sql = u"""update mapping_res_tenant_ref a set a.`status` = null  where a.resource_id =:target_id
                     and a.`status` = :status and a.tenant_id = :tenant_id
                       """
        db.session.execute(text(sql), {'target_id': target_id, 'status': status, 'tenant_id': tenant_id})

    @classmethod
    def delete_tenant_ip(cls, target_id, tenant_id):
        """
        删除公网ip与租户关联关系
        :param target_id:
        :param tenant_id:
        :return:
        """
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        sql = u"""update mapping_res_tenant_ref a set a.`removed` = :removed  where a.resource_id =:target_id
                         and a.`tenant_id` = :tenant_id
                           """
        db.session.execute(text(sql), {'target_id': target_id, 'removed': removed, 'tenant_id': tenant_id})

    @classmethod
    def remove_cmdb_ip(cls, target_id):
        """
        更新cmdb公网ip的状态为空闲
        :param target_id:
        :return:
        """
        status = IpStatus.free
        sql = u"""update cmdb_internet_ip a set a.`status` = :status  where a.id =:target_id
                           """
        db.session.execute(text(sql), {'target_id': target_id, 'status': status})

    @classmethod
    def check_delete_ip(cls, target_id, tenant_id):
        """
        判断ip是否已绑定内网（排除绑定中的）cmdb表中是预分配，net_internet_ip状态为null
        :param target_id:
        :param tenant_id:
        :return:
        """
        sql = u"""select * from net_internet_ip a where a.tenant_id = :tenant_id and a.target_id = :target_id
              and a.removed is null
                              """
        data = db.session.execute(text(sql), {'target_id': target_id, 'tenant_id': tenant_id})
        return data

    @classmethod
    def get_ip_for_bound(cls, tenant_id):
        """
         获取租户下预分配的公网ip（除去1.回收站中的，2.正在绑定中的，3.已绑定的）
         sql 分析查询mapping_res_tenant_ref表中的status是空且removed是空的，且不再net_internet_ip表中的（正在绑定
         和已绑定的）且cmdb表中不是使用中的（防止数据错误，此处条件省略也可）
        :param tenant_id:
        :return:
        """
        status = IpStatus.using
        resource_type = ResourceType.PUBLIC_IP.value
        sql = u"""select b.* from mapping_res_tenant_ref a , cmdb_internet_ip b where a.tenant_id = :tenant_id
                and a.resource_type = :resource_type
                and a.status is null and a.removed is null and a.resource_id not in
                (select target_id from net_internet_ip  where removed is null and `status` is null or `status` = 'executing')
                and a.resource_id not in
                (select id from cmdb_internet_ip where `status`=:status) and a.resource_id = b.id
                                 """
        data = db.session.execute(text(sql), {'resource_type': resource_type, 'status': status,
                                              'tenant_id': tenant_id})
        return data

    @classmethod
    def get_logic_object(cls, tenant_id):
        """
         获取租户下虚机的内网ip(进回收站和已删除的除外)
         通过租户id查询关联的虚机，在查关联的ip，然后查虚机的名称，查ip地址
        :param tenant_id:
        :return:
        """
        status = IpStatus.expunge
        resource_type = BoundObjectType.host_logicserver
        sql = u""" select b.name as object,d.id as source_ip_id ,d.addr as source_ip, b.type from mapping_res_tenant_ref a,cmdb_host_logicserver b,
                 mapping_host_ip_ref c, cmdb_ip d where tenant_id=:tenant_id and a.removed is null and b.removed is NULL
                 and b.`status` != 'expung' and
                resource_type = :resource_type and a.resource_id = b.id and b.id = c.host_id and d.id=c.ip_id
                                     """
        data = db.session.execute(text(sql), {'resource_type': resource_type, 'status': status,
                                              'tenant_id': tenant_id})
        return data

    @classmethod
    def get_pm_object(cls, tenant_id):
        """
         获取租户下物理机的内网ip(进回收站和已删除的除外)
         通过租户id查询关联的虚机，在查关联的ip，然后查虚机的名称，查ip地址
        :param tenant_id:
        :return:
        """
        status = IpStatus.expunge
        resource_type = BoundObjectType.PM
        sql = u""" select b.name as object,d.id as source_ip_id ,d.addr as source_ip, b.type from mapping_res_tenant_ref a,cmdb_host_logicserver b,
                     mapping_host_ip_ref c, cmdb_ip d where tenant_id=:tenant_id and a.removed is null and b.removed is NULL
                     and b.`status` != :status and b.status = 'running' and
                    resource_type = :resource_type and a.resource_id = b.id and b.id = c.host_id and d.id=c.ip_id
                                         """
        data = db.session.execute(text(sql), {'resource_type': resource_type, 'status': status,
                                              'tenant_id': tenant_id})
        return data

    @classmethod
    def get_f5lb_object(cls, tenant_id):
        """
         获取租户下负载均衡的内网ip(进回收站和已删除的除外)
         根据租户id查租户下的vpc_id，关联负载均衡，查vip地址
        :param tenant_id:
        :return:
        """
        vip = NatType.vip
        sql = u"""select b.name as object, c.id as source_ip_id ,c.addr as source_ip ,:vip as type
                from net_vpc a , net_f5_lbpolicy b ,cmdb_loadbalance_ip c
                where a.id = b.vpc_id and b.vip_id = c.id and a.tenant_id = :tenant_id
                and b.removed is null and b.`status` is null
                                      """
        data = db.session.execute(text(sql), {'tenant_id': tenant_id, 'vip': vip})
        return data

    @classmethod
    def update_nat(cls, args):
        """
         修改nat 名称及描述 根据租户的id及公网ip_id
        :return:
        """
        sql = u"""update net_internet_ip a set a.name = :name ,a.description = :description where
                a.target_id = :target_id and a.tenant_id = :tenant_id
                                          """
        db.session.execute(text(sql), args)

    @classmethod
    def check_update_nat_name(cls, args):
        """
         修改时检查nat是否重名，根据租户的id和名字，target_id
        :param args:
        :return:
        """
        vip = NatType.vip
        sql = u"""select * from net_internet_ip a where a.target_id != :target_id and a.tenant_id = :tenant_id
                and a.`name` = :name
                                         """
        data = db.session.execute(text(sql), args)
        return data

    @classmethod
    def check_nat_name(cls, args):
        """
         绑定时检查nat是否重名，根据租户的id和名字
        :param args:
        :return:
        """
        sql = u"""select * from net_internet_ip a where a.tenant_id = :tenant_id
                    and a.`name` = :nat_name and a.removed is NULL
                                             """
        data = db.session.execute(text(sql), args)
        return data

    @classmethod
    def bound_ip_start(cls, args):
        """
         在net_internet_ip中插入数据正在执行中
        :return:
        """
        now = datetime.datetime.now()
        args['created'] = now.strftime("%Y-%m-%d %H:%M:%S")
        sql = u"""insert into net_internet_ip (`name`, `type`, target_id, source_ip,`status`, description, created,
                    source_ip_id, tenant_id, port, export_type, export_velocity)
                VALUES (:nat_name, :type, :target_id, :source_ip, :status, :description, :created, :source_ip_id, :tenant_id,
                    :port, :export_type, :export_velocity)"""
        db.session.execute(text(sql), args)
        db.session.commit()

    @classmethod
    def unbound_ip_start(cls, status, target_id, source_ip_id):
        """
         在net_internet_ip中插入数据正在执行中
        :return:
        """
        sql = u"""update net_internet_ip set `status`=:status where target_id =:target_id and source_ip_id =:source_ip_id
                                                """
        db.session.execute(text(sql), {'status':status, 'target_id':target_id, 'source_ip_id':source_ip_id})
        db.session.commit()

    @classmethod
    def bound_ip_finish(cls, target_id, source_ip_id, tenant_id):
        """
         绑定公网ip工单执行成功
        :return:
        """
        sql = u"""update net_internet_ip set status = null where target_id = :target_id and source_ip_id =:source_ip_id
                  and tenant_id = :tenant_id
                                                """
        db.session.execute(text(sql), {'target_id': target_id, 'source_ip_id': source_ip_id, 'tenant_id': tenant_id})
        db.session.commit()

    @classmethod
    def unbound_ip_finish(cls, target_id, source_ip_id, tenant_id):
        """
         解绑公网ip工单执行成功
        :return:
        """
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        sql = u"""update net_internet_ip set removed =:removed ,`status` = null where target_id = :target_id and source_ip_id =:source_ip_id
                      and tenant_id = :tenant_id
                                                    """
        db.session.execute(text(sql), {'target_id': target_id, 'source_ip_id': source_ip_id,
                                       'tenant_id': tenant_id, 'removed': removed})
        db.session.commit()

