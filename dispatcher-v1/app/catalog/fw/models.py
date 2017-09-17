# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import text

from app.configs.code import ResponseCode
from app.configs.default import DefaultConfig
from app.extensions import db
from app.utils.database import CRUDMixin
from app.process.constant import IfProcess, NodeType
from app.utils.format import format_result
from app.utils.response import res


class fw(CRUDMixin):
    @staticmethod
    def get_app_resource(args):
        # modify by gsliu
        sql = u"""select una.* FROM (
              SELECT ten.tenant_id, t.name,t.hypervisor_type, t2.location, t2.addr, t.type,ten.resource_type,t.logicpool_id,nvpc.id AS vpc_id, nvpc.vpc_name,t.created  FROM cmdb_host_logicserver t
              left join mapping_res_tenant_ref ten on ten.resource_type  in ('host_logicserver','PM') and ten.resource_id = t.id
              LEFT JOIN mapping_host_ip_ref t1 on t1.host_id = t.id
              LEFT JOIN cmdb_ip t2 on t2.id = t1.ip_id
              LEFT JOIN net_subnet nsu ON nsu.segment_id = t2.segment_id
              LEFT JOIN net_vpc nvpc ON nvpc.id = nsu.vpc_id
              WHERE t.status not in ('destroy','deleting','creating','expung') and nsu.removed is null and ten.tenant_id = :tenant_id

              union all

              SELECT ten.tenant_id, log.name,log.hypervisor_type, ip.location, ip.addr, log.type,ten.resource_type,log.logicpool_id,nvpc.id AS vpc_id, nvpc.vpc_name,log.created FROM cmdb_internet_ip ip
              left join mapping_res_tenant_ref ten on ten.resource_type  in ('PUBLIC_IP') and ten.resource_id = ip.id
              LEFT JOIN mapping_host_ip_ref t1 on t1.ip_id = ip.id
              left join cmdb_host_logicserver log on t1.host_id = log.id
              LEFT JOIN cmdb_ip t2 on t2.id = t1.ip_id
              LEFT JOIN net_subnet nsu ON nsu.segment_id = t2.segment_id
              LEFT JOIN net_vpc nvpc ON nvpc.id = nsu.vpc_id
              WHERE ip.status in ('预分配') and nsu.removed is null and ten.tenant_id = :tenant_id
              ) una
              """
        if args['type'] == 'vm':
            sql = u''.join([sql, u""" WHERE una.type='vm' AND una.resource_type='host_logicserver'"""])
        elif args['type'] == 'pm':
            sql = u''.join([sql, u""" WHERE una.type='pm' AND una.resource_type='PM'"""])
        elif args['type'] == 'PUBLIC_IP':
            sql = u''.join([sql, u""" WHERE una.resource_type = 'PUBLIC_IP'"""])
        sql = u''.join([sql, u"""  ORDER BY una.created desc"""])
        res = db.session.execute(text(sql), {'tenant_id': args['tenant_id']})
        res = format_result(res)
        return res

class DisFw(db.Model, CRUDMixin):
    __tablename__ = 'net_firewall_policy'

    id = db.Column(db.Integer, primary_key=True)
    vpc_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(32, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    type = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    security_group_policy_id = db.Column(db.Integer, nullable=False, server_default=text("'0'"))
    v_firewall_policy_id = db.Column(db.Integer, nullable=False, server_default=text("'0'"))
    device_cluster_id = db.Column(db.Integer, nullable=False)
    source_ip_addr = db.Column(db.String(40, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    target_ip_addr = db.Column(db.String(40, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    source_port_range = db.Column(db.String(256, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    target_port_addr = db.Column(db.String(256, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    protocol = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    # permit/deny
    action = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    ip_version = db.Column(db.String(32, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), server_default=text("'Ipv4'"))
    description = db.Column(db.Text)
    status = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @staticmethod
    def get_fw(args):

        """
            wyj
            功能：我的订单 （根据用户ID来查询订单列表）
        """
        expung_sql = ''
        if args['keyword']:
            if args['recycle'] == 1:
                expung_sql = u" and a.status = 'expunge' "
            else:
                expung_sql = u" and a.status != 'expunge' "
        else:
            if args['recycle'] == 1:
                expung_sql = u" and a.status = 'expunge' "
            else:
                expung_sql = u" and a.status != 'expunge' "
        sql = u"""SELECT a.id, a.name,a.status,a.protocol,a.action,a.source_ip_addr,a.target_ip_addr,a.virtual_fw_policy_id,a.direction,
                a.physical_fw_policy_id,a.sg_policy_id, a.source_port_range,a.target_port_addr,a.created,a.description,a.ip_version
                from net_firewall_policy_main a LEFT JOIN net_vpc vpc on a.vpc_id = vpc.id
                where vpc.tenant_id = :tenant_id and a.removed is null AND a.status = 'succeed'
                  """
        if args['keyword']:
            if 'name' in args['keyword'] and args['keyword']['name']:
                sql += """ and a.name like '%""" + args['keyword']['name'] + """%'"""
            if 'direction' in args['keyword'] and args['keyword']['direction']:
                sql += """ and a.direction = '""" + args['keyword']['direction'] + """'"""
            if 'protocol' in args['keyword'] and args['keyword']['protocol']:
                sql += """ and a.protocol = '""" + args['keyword']['protocol'] + """'"""
            if 'action' in args['keyword'] and args['keyword']['action']:
                sql += """ and a.action = '""" + args['keyword']['action'] + """'"""
            if 'source_ip_addr' in args['keyword'] and args['keyword']['source_ip_addr']:
                sql += """ and a.source_ip_addr  like '%""" + args['keyword']['source_ip_addr'] + """%'"""
            if 'target_ip_addr' in args['keyword'] and args['keyword']['target_ip_addr']:
                sql += """ and a.target_ip_addr  like '%""" + args['keyword']['target_ip_addr'] + """%'"""
            if 'source_port_range' in args['keyword'] and args['keyword']['source_port_range']:
                sql += """ and a.source_port_range  like '%""" + args['keyword']['source_port_range'] + """%'"""
            if 'target_port_addr' in args['keyword'] and args['keyword']['target_port_addr']:
                sql += """ and a.target_port_addr  like '%""" + args['keyword']['target_port_addr'] + """%'"""

            if 'ip' in args['keyword'] and args['keyword']['ip']:
                sql += """ and (a.source_ip_addr like '%""" + args['keyword']['ip'] + """%' or"""  + """ a.target_ip_addr like '%""" + args['keyword']['ip'] + """%')"""

        limit = u""" order by a.id desc limit :start, :per_page """
        fw_list = db.session.execute(text(u''.join([sql,expung_sql, limit])),args)
        return fw_list

    @staticmethod
    def recycle_fw(fw_id):

        sql_update = u"""
                    UPDATE net_firewall_policy SET `status`=:status
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': fw_id, 'status': 'expunge'})
        db.session.commit()

    @staticmethod
    def recover_fw(fw_id):

        sql_update = u"""
                    UPDATE net_firewall_policy SET `status`=null
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': fw_id})
        db.session.commit()

    @staticmethod
    def get_task_id(order_id):
        sql = u"""
              SELECT id FROM com_async_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format_result(res)
        return res

    @staticmethod
    def get_count(tenant_id, resource_type=u'firewall',expung = None,keyword=None):
        expung_sql = ''
        if expung:
            expung_sql = u" AND a.status = 'expunge' "
        else:
            expung_sql = u" AND a.status != 'expunge' "
        count = 0

        sql = u"""SELECT count(a.id) as te
                from net_firewall_policy_main a LEFT JOIN net_vpc vpc on a.vpc_id = vpc.id
                where vpc.tenant_id = :tenant_id and a.removed is null AND a.status = 'succeed'
                  """
        if keyword:
            if 'name' in keyword and keyword['name']:
                sql += """ and a.name like '%""" + keyword['name'] + """%'"""
            if 'direction' in keyword and keyword['direction']:
                sql += """ and a.direction = '""" + keyword['direction'] + """'"""
            if 'protocol' in keyword and keyword['protocol']:
                sql += """ and a.protocol = '""" + keyword['protocol'] + """'"""
            if 'action' in keyword and keyword['action']:
                sql += """ and a.action = '""" + keyword['action'] + """'"""
            if 'source_ip_addr' in keyword and keyword['source_ip_addr']:
                sql += """ and a.source_ip_addr  like '%""" + keyword['source_ip_addr'] + """%'"""
            if 'target_ip_addr' in keyword and keyword['target_ip_addr']:
                sql += """ and a.target_ip_addr  like '%""" + keyword['target_ip_addr'] + """%'"""
            if 'source_port_range' in keyword and keyword['source_port_range']:
                sql += """ and a.source_port_range  like '%""" + keyword['source_port_range'] + """%'"""
            if 'target_port_addr' in keyword and keyword['target_port_addr']:
                sql += """ and a.target_port_addr  like '%""" + keyword['target_port_addr'] + """%'"""

            if 'ip' in keyword and keyword['ip']:
                sql += """ and (a.source_ip_addr like '%""" + keyword['ip'] + """%' or""" + """ a.target_ip_addr like '%""" + keyword['ip'] + """%')"""

        res = db.session.execute(text(u''.join([sql,expung_sql])),{'tenant_id':tenant_id })
        for i in res:
            count = i.te
            return count

    @staticmethod
    def update_name_by_id(args):
        try:
            sql = u""" update net_firewall_policy_main set name = :name, description = :description where id = :id"""
            db.session.execute(sql, args)
            return res(ResponseCode.SUCCEED, u'修改成功!')
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @staticmethod
    def get_fw_id(fwid):
        print fwid
        sql = u"""
              SELECT vfw.name as vfw_name,sg.name as sg_name,fw.name as fw_name,main.virtual_fw_policy_id,main.sg_policy_id, main.physical_fw_policy_id,vpc.vpc_name FROM net_firewall_policy_main main
              left join net_v_firewall_policy vfw on vfw.id = main.virtual_fw_policy_id
              LEFT JOIN net_security_group_policy sg on sg.id = main.sg_policy_id
              LEFT JOIN net_firewall_policy fw on fw.id = main.physical_fw_policy_id
              left join net_vpc vpc on vpc.id = main.vpc_id
              WHERE main.id = :id
              """
        res = db.session.execute(text(sql), {'id':fwid})
        res = format_result(res)
        return res


    @staticmethod
    def update_fwmain_status(id):
        sql_update = u"""
                    UPDATE net_firewall_policy_main SET `status`= 'deleting'
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': id})
