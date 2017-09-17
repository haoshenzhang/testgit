# -*- coding: utf-8 -*-

from sqlalchemy import text
from app.configs.default import DefaultConfig
from app.extensions import db
from app.utils.database import CRUDMixin
from app.process.constant import IfProcess, NodeType
from app.utils.format import format_result




class f5(CRUDMixin):
    @staticmethod
    def get_app_resource(tenant_id,app_id):
        sql = u"""
              SELECT ten.tenant_id,t.name,t.id as host_id, t.hypervisor_type, t2.id as ip_id, t2.location, t2.addr, t.type,t.logicpool_id,sub.id as net_subnet_id,sub.name as net_subnet_name FROM cmdb_host_logicserver t
              left join mapping_res_tenant_ref ten on ten.resource_type in ('host_logicserver','PM') and ten.resource_id = t.id
              LEFT JOIN mapping_host_ip_ref t1 on t1.host_id = t.id
              LEFT JOIN cmdb_ip t2 on t2.id = t1.ip_id
              LEFT JOIN net_subnet sub on sub.segment_id =t2.segment_id
              WHERE t.status not in ('destroy','deleting','creating','expung') and sub.status not in ('deleting') and ten.tenant_id = :tenant_id and t.application_id = :app_id
              """
        res = db.session.execute(text(sql), {'tenant_id': tenant_id,'app_id': app_id})
        res = format_result(res)
        return res

class DisF5(db.Column,CRUDMixin):
    __tablename__ = "net_f5_lbpolicy"
    # id
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # 关联的vpc表id（目前和租户一对一）
    vpc_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(32, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    f5cluster_id = db.Column(db.Integer, nullable=False)
    #net_loadbalance_ip表的id
    vip_id = db.Column(db.Integer, nullable=False)
    # 应用类型  http/tcp
    apptype = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    protocol = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    external_port = db.Column(db.Integer, nullable=False)
    host_port = db.Column(db.Integer, nullable=False)
    lb_method = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    persist_method = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    health_method = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    ssl_enable = db.Column(db.String(10, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False, server_default=text("'disable'"))
    timeout = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE))
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @staticmethod
    def get_f5(args):

        """
            wyj
            功能：我的订单 （根据用户ID来查询订单列表）
        """
        expung_sql = ''
        if args['keyword']:
            if args['recycle'] == 1:
                expung_sql = u"and a.status = 'expunge' "
            else:
                expung_sql = u"and a.status is null "
        else:
            if args['recycle'] == 1:
                expung_sql = u"having a.status = 'expunge' "
            else:
                expung_sql = u"having a.status is null "

        sql = u"""
                  select a.id, a.name as name,a.status,a.created,a.persistmethod,a.ssl_enable,a.apptype,a.protocol, a.vip as vip, GROUP_CONCAT(a.ip) as ip,GROUP_CONCAT(a.host) as host,a.external_port as external_port,a.description,a.app_name,a.application_id,a.source_ip,a.type,a.removed
              from (
              SELECT distinct lb.id, lb.name,lb.status,lb.created,lb.persist_method as persistmethod,lb.ssl_enable,lb.apptype,lb.protocol,ip.addr as vip,ip1.addr as ip ,lb.external_port,log.name as host,lb.description, app.name as app_name,log.application_id,int_ip.source_ip,int_ip.type,int_ip.removed FROM net_f5_lbpolicy lb
              LEFT JOIN net_vpc vpc on lb.vpc_id = vpc.id
              LEFT JOIN cmdb_mapping_res_f5lb mlb on mlb.f5lbpolicy_id = lb.id and mlb.res_type = 'logic'
              LEFT JOIN cmdb_host_logicserver log on mlb.res_id = log.id
              LEFT JOIN mapping_host_ip_ref host_ip on host_ip.host_id = log.id
              LEFT JOIN cmdb_loadbalance_ip ip on lb.vip_id = ip.id
              LEFT JOIN cmdb_ip ip1 on ip1.id =host_ip.ip_id
              LEFT JOIN biz_application app on app.id = log.application_id
              LEFT JOIN net_internet_ip int_ip on int_ip.type='vip' and int_ip.source_ip_id = lb.vip_id and int_ip.removed is null
              where vpc.tenant_id = :tenant_id and lb.removed is null )a
              GROUP BY a.id desc
                  """
        if args['keyword']:
            sbsql = ''
            for k,v in args['keyword'].items():
                sbsql += """and ("""+ k +""" like '%""" + v + """%')"""
            sbsql = sbsql[3:]
            sbsql = """having """ + sbsql
            sql = sql+sbsql
        limit = u""" limit :start, :per_page"""


        f5_list = db.session.execute(text(u''.join([sql,expung_sql, limit])),args)
        return f5_list

    @staticmethod
    def recycle_f5(f5_id):

        sql_update = u"""
                    UPDATE net_f5_lbpolicy SET `status`=:status
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': f5_id, 'status': 'expunge'})
        db.session.commit()

    @staticmethod
    def recover_f5(f5_id):

        sql_update = u"""
                    UPDATE net_f5_lbpolicy SET `status`=null
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': f5_id})
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
    def get_count(tenant_id, resource_type=u'f5_lbpolicy',expung=None,keyword=None):
        expung_sql = ''
        if keyword:
            if expung == True:
                expung_sql = u"and a.status = 'expunge' "
            else:
                expung_sql = u"and a.status is null "
        else:
            if expung == True:
                expung_sql = u"having a.status = 'expunge' "
            else:
                expung_sql = u"having a.status is null "

        sql = u"""
        select a.id, a.name as name,a.status,a.created,a.persistmethod,a.ssl_enable,a.apptype,a.protocol, a.vip as vip, GROUP_CONCAT(a.ip) as ip,GROUP_CONCAT(a.host) as host,a.external_port as external_port ,a.description,a.app_name,a.application_id,a.source_ip,a.type,a.removed
              from (
              SELECT distinct lb.id, lb.name,lb.status,lb.created,lb.persist_method as persistmethod,lb.ssl_enable,lb.apptype,lb.protocol,ip.addr as vip,ip1.addr as ip ,lb.external_port,log.name as host,vpc.description, app.name as app_name,ord.application_id,int_ip.source_ip,int_ip.type,int_ip.removed FROM net_f5_lbpolicy lb
              LEFT JOIN net_vpc vpc on lb.vpc_id = vpc.id
              LEFT JOIN cmdb_mapping_res_f5lb mlb on mlb.f5lbpolicy_id = lb.id and mlb.res_type = 'logic'
              LEFT JOIN cmdb_host_logicserver log on mlb.res_id = log.id
              LEFT JOIN mapping_host_ip_ref host_ip on host_ip.host_id = log.id
              LEFT JOIN cmdb_loadbalance_ip ip on lb.vip_id = ip.id
              LEFT JOIN cmdb_ip ip1 on ip1.id =host_ip.ip_id
              LEFT JOIN dis_order ord on ord.tenant_id = vpc.tenant_id and ord.resource_type = 'LB_Policy' and ord.status='succeed' and ord.operation_type = 'create'
              LEFT JOIN biz_application app on app.id = ord.application_id
              LEFT JOIN net_internet_ip int_ip on int_ip.type='vip' and int_ip.source_ip_id = lb.vip_id and int_ip.removed is null
              where vpc.tenant_id = :tenant_id and lb.removed is null )a
              GROUP BY a.id desc
            """

        if keyword:
            sbsql = ''
            for k,v in keyword.items():
                sbsql += """and ("""+ k +""" like '%""" + v + """%')"""
            sbsql = sbsql[3:]
            sbsql = """having """ + sbsql
            sql = sql+sbsql
        limit = u""" limit :start, :per_page"""

        res = db.session.execute(text(u''.join([sql, expung_sql])),{'tenant_id': tenant_id})
        res = format_result(res)
        count = 0
        if res:
            print res
            count = len(res)

        return count

