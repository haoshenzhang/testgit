# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    虚拟机cmdb
"""

from app.deployment.models import ComAsyncTask
from app.extensions import db
from sqlalchemy import text
from app.utils.database import CRUDMixin
from app.utils.format import FormatService
from app.utils.format import format_result
from app.catalog.volume.models import CmdbVolume
from flask import current_app


class CmdbF5(db.Model, CRUDMixin):
    __tablename__ = 'cmdb_ip'

    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(50), nullable=False)
    segment_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(u'使用中', u'预分配', u'注销', u'空闲', u'删除', u'预留'), nullable=False)
    usage = db.Column(db.Enum(u'生产', u'预投产', u'测试', u'UAT', u'办公'), nullable=False)
    network = db.Column(db.Enum(u'内网', u'内网DMZ', u'InternetDMZ', u'企业互联DMZ', u'测试', u'大数据', u'管理', u'其他', u'办公网段'), nullable=False)
    app_net = db.Column(db.Enum(u'传统业务系统', u'新一代共享系统', u'新一代CA专属系统', u'新一代MU专属系统', u'新一代CZ专属系统', u'新一代其它专属系统', u'无限制'), nullable=False)
    app_level = db.Column(db.Enum(u'高等级', u'差异化', u'无限制'))
    app_category = db.Column(db.Enum('WEB', 'APP', 'DB', u'无限制', 'APP_DB', 'LB'))
    type = db.Column(db.Enum(u'物理机IP', u'虚拟机IP', u'服务IP', 'NASIP', u'设备管理IP', u'监控管理IP', u'负载均衡', 'SCAN IP', u'应用IP'), nullable=False)
    location = db.Column(db.Enum(u'东四', u'三里屯', u'国富瑞', u'嘉兴',u'后沙峪'), nullable=False)
    class_ = db.Column(db.Enum('HOSTIP', 'NASIP', u'负载均衡IP'))
    coss_id = db.Column(db.Integer, nullable=False)
    relationship_id = db.Column(db.Integer, nullable=False)
    
    __tablename__ = 'cmdb_loadbalance_ip'
    
    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(50), nullable=False)
    segment_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(u'使用中', u'预分配', u'注销', u'空闲', u'删除', u'预留'), nullable=False)
    usage = db.Column(db.Enum(u'生产', u'预投产', u'测试', u'UAT', u'办公'), nullable=False)
    network = db.Column(db.Enum(u'内网', u'内网DMZ', u'InternetDMZ', u'企业互联DMZ', u'测试', u'大数据', u'管理', u'其他', u'办公网段'), nullable=False)
    app_net = db.Column(db.Enum(u'传统业务系统', u'新一代共享系统', u'新一代CA专属系统', u'新一代MU专属系统', u'新一代CZ专属系统', u'新一代其它专属系统', u'无限制'), nullable=False)
    app_level = db.Column(db.Enum(u'高等级', u'差异化', u'无限制'))
    app_category = db.Column(db.Enum('WEB', 'APP', 'DB', u'无限制', 'APP_DB', 'LB'))
    type = db.Column(db.Enum(u'物理机IP', u'虚拟机IP', u'服务IP', 'NASIP', u'设备管理IP', u'监控管理IP', u'负载均衡', 'SCAN IP', u'应用IP'), nullable=False)
    location = db.Column(db.Enum(u'东四', u'三里屯', u'国富瑞', u'嘉兴',u'后沙峪'), nullable=False)
    class_ = db.Column(db.Enum('HOSTIP', 'NASIP', u'负载均衡IP'))
    coss_id = db.Column(db.Integer, nullable=False)
    relationship_id = db.Column(db.Integer, nullable=False)

   
    @staticmethod
    def select_ip_info(addr):
        sql = u"""
                SELECT id, network,coss_id FROM cmdb_loadbalance_ip
                WHERE addr = :addr
                """
        res = db.session.execute(text(sql), {'addr': addr})
        res = format_result(res)
        return res[0]
        
    @staticmethod
    def update_status(args):
       sql_update = u"""
                    UPDATE cmdb_loadbalance_ip SET status = :status
                    WHERE id = :id
                    """
       db.session.execute(text(sql_update),args)
       db.session.commit()
       
       
    @staticmethod
    def insert_ref(args):
        sql = u""" insert into mapping_res_tenant_ref(tenant_id, resource_type, resource_id, created)
                          VALUES(:tenant_id, :resource_type, :resource_id, :created) """
        db.session.execute(sql, args)

    @staticmethod
    def select_vip_info(id):
        sql = u"""
                  SELECT ip.id,ip.addr as vip,ip.network,ip.coss_id FROM net_f5_lbpolicy lb
                  left join cmdb_loadbalance_ip ip on ip.id = lb.vip_id
                  where lb.id = :id
                  """
        res = db.session.execute(text(sql), {'id': id})
        res = format_result(res)
        print res
        return res[0]

    @staticmethod
    def select_vip_info1(id):
        sql = u"""
                  SELECT ip.id,ip.addr as vip,ip.network,ip.coss_id FROM net_f5_lbpolicy lb
                  left join cmdb_loadbalance_ip ip on ip.id = lb.vip_id
                  where lb.id = :id
                  """
        res = db.session.execute(text(sql), {'id': id})
        res = format_result(res)
        print res
        return res[0]

    @staticmethod
    def select_f5_id(addr):
        sql = u"""
                  SELECT lb.id, lb.name FROM net_f5_lbpolicy lb
                  left join cmdb_loadbalance_ip ip on ip.id = lb.vip_id
                  where ip.addr = :addr and lb.removed is null and lb.status is null
                  """
        res = db.session.execute(text(sql), {'addr': addr})
        res = format_result(res)
        return res[0]

    @staticmethod
    def select_task_result(order_id):
        sql = u"""
                  SELECT result FROM com_async_task task
                  where order_id = :order_id
                  """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format_result(res)
        return res[0]

    @staticmethod
    def select_host(addr):
        sql = u"""
                  SELECT log.id FROM cmdb_ip ip
                  LEFT JOIN mapping_host_ip_ref host_ip on ip.id =host_ip.ip_id
                  LEFT JOIN cmdb_host_logicserver log on log.id=host_ip.host_id
                  where ip.addr = :addr
                  """
        res = db.session.execute(text(sql), {'addr': addr})
        res = format_result(res)

        return res[0]
    
    @staticmethod
    def insert_f5(args):
        sql = u""" insert into cmdb_mapping_res_f5lb(res_type, res_id, f5lbpolicy_id)
                          VALUES(:res_type, :res_id, :f5lbpolicy_id) """
        db.session.execute(sql, args)
        
    @staticmethod
    def delete_f5_mapping(f5lbpolicy_id):
        sql = u""" delete from cmdb_mapping_res_f5lb
                    where f5lbpolicy_id = :f5lbpolicy_id"""
        db.session.execute(text(sql), {'f5lbpolicy_id': f5lbpolicy_id})
        