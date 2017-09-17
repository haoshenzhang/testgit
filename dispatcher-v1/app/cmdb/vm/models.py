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


class CmdbHostLogicserver(db.Model, CRUDMixin):
    __tablename__ = 'cmdb_host_logicserver'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50))
    cpu = db.Column(db.Integer, nullable=False)
    mem = db.Column(db.Integer, nullable=False)
    os_type = db.Column(db.String(50), nullable=False)
    hypervisor_type = db.Column(db.String(50))
    type = db.Column(db.String(20), nullable=False)
    logicpool_id = db.Column(db.Integer, nullable=False)
    physic_pool_id = db.Column(db.Integer)
    internal_id = db.Column(db.String(64))
    coss_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    description = db.Column(db.String(256))
    status = db.Column(db.String(20), nullable=False)
    offeringid = db.Column(db.Integer, nullable=False)
    pm_cluster_id = db.Column(db.Integer, nullable=False)

    @staticmethod
    def insert_logicserver_ci(**kwargs):
        try:
            sql_insert = u"""
                    INSERT INTO cmdb_host_logicserver(`application_id`, `name`, `password`,
                        `cpu`, `mem`,`os_type`,`hypervisor_type`, `type`,`logicpool_id`,
                        `physic_pool_id`,`internal_id`,`coss_id`,`created`,`host_name`,
                        `status`,`offeringid`,`application_name`,`trusteeship`,`os_template_id`)
                    VALUES (:application_id, :name, :password, :cpu, :mem, :os_type, :hypervisor_type,
                     :type, :logicpool_id, :physic_pool_id, :internal_id, :coss_id, :created, :host_name,
                       :status, :offeringid, :application_name, :trusteeship, :os_template_id)
                    """
            host_logicserver_result = db.session.execute(text(sql_insert), kwargs['dict_'])
            host_id = host_logicserver_result.lastrowid
            return host_id
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @staticmethod
    def insert_ref(args):
        sql = u""" insert into mapping_res_tenant_ref(tenant_id, resource_type, resource_id, created)
                          VALUES(:tenant_id, :resource_type, :resource_id, :created) """
        db.session.execute(sql, args)

    @staticmethod
    def insert_ip_host_res(args):
        sql = u""" insert into mapping_host_ip_ref(host_id, ip_id, ref_type)
                                  VALUES(:host_id, :ip_id, :ref_type) """
        db.session.execute(sql, args)

    @staticmethod
    def insert_order_ref(args):
        sql = u""" insert into dis_mapping_res_order(order_id, resource_type, resource_id)
                          VALUES(:order_id, :resource_type, :resource_id) """
        db.session.execute(sql, args)

    @staticmethod
    def get_ip_id(args):
        sql = u"""
                SELECT id  FROM cmdb_ip  WHERE addr = :addr
            """
        ip_id_ = db.session.execute(text(sql), args)
        ip_id = format_result(ip_id_)[0]['id']
        return ip_id

    @staticmethod
    def get_ip_by_ip_id(args):
        sql = u"""
                SELECT addr  FROM cmdb_ip  WHERE id = :id
            """
        ip_id_ = db.session.execute(text(sql), args)
        ip_id = format_result(ip_id_)[0]['addr']
        return ip_id

    @staticmethod
    def get_ip_id_by_ref(args):
        args_dict = dict(
            host_id = args
        )
        sql = u"""
                    SELECT *  FROM mapping_host_ip_ref  WHERE host_id = :host_id
                """
        res = db.session.execute(text(sql), args_dict)
        res = format_result(res)[0]['ip_id']
        return res

    @staticmethod
    def release_ip(ip_id):
        args = dict(
            ip_id = ip_id,
            status=u"空闲"
        )
        sql_update = u"""
                    UPDATE cmdb_ip SET status = :status
                    WHERE id = :ip_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def update_ip_status(args):
        sql_update = u"""
                    UPDATE cmdb_host_logicserver SET name = :name, description = :description
                    WHERE internal_id = :internal_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def get_ip_coss_id(args):
        sql = u"""
                SELECT coss_id  FROM cmdb_ip  WHERE addr = :addr
            """
        ip_coss_id_ = db.session.execute(text(sql), args)
        ip_coss_id = format_result(ip_coss_id_)[0]['coss_id']
        return ip_coss_id

    @staticmethod
    def update_vm_info(args):
        sql_update = u"""
                    UPDATE cmdb_host_logicserver SET name = :name, description = :description
                    WHERE id = :id
                    """
        db.session.execute(text(sql_update),args)
        db.session.commit()

    @staticmethod
    def update_vm_status(args):
        """
        vmstart , stop等状态
        :param args:
        :return:
        """
        sql_update = u"""
                    UPDATE cmdb_host_logicserver SET status = :status
                    WHERE internal_id = :internal_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def update_vm_removed(args):
        """
        vmstart , stop等状态
        :param args:
        :return:
        """
        sql_update = u"""
                    UPDATE cmdb_host_logicserver SET removed = :removed
                    WHERE internal_id = :internal_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def remove_volume(args):
        sql_update = u"""
                    UPDATE cmdb_volume SET removed = :removed
                    WHERE logicserver_id = :logicserver_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()


    @staticmethod
    def remove_host_ref(args):
        sql_update = u"""
                    UPDATE mapping_res_tenant_ref SET removed = :removed
                    WHERE resource_type = :resource_type AND resource_id = :resource_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def remove_ip_ref(args):
        sql_update = u"""
                    UPDATE mapping_res_tenant_ref SET removed = :removed
                    WHERE resource_type = :resource_type AND resource_id = :resource_id
                    """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def remove_volume_ref(args):
        sql_update = u"""
                        UPDATE mapping_res_tenant_ref SET removed = :removed
                        WHERE resource_type = :resource_type AND resource_id = :resource_id
                        """
        db.session.execute(text(sql_update), args)
        db.session.commit()

    @staticmethod
    def vm_detail_by_id(**kwargs):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h WHERE internal_id = :internal_id
            """
        os_list = db.session.execute(text(sql),{'internal_id':kwargs['uuid']})
        return os_list

    @staticmethod
    def vm_detail(**kwargs):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h WHERE id= :id AND name= :name
            """
        os_list = db.session.execute(text(sql))
        return os_list

    @staticmethod
    def vm_detail_pro(**kwargs):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h
            """
        os_list = db.session.execute(text(sql))
        return os_list

    @staticmethod
    def get_vm_info_by_uuid(uuid):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h WHERE internal_id= :internal_id
            """
        os_list = db.session.execute(text(sql),{'internal_id':uuid})
        os_list = FormatService.format_result(os_list)
        return os_list

    @staticmethod
    def get_vm_info_by_vm_id(uuid):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h WHERE id= :id
            """
        os_list = db.session.execute(text(sql), {'id': uuid})
        os_list = format_result(os_list)
        return os_list

    @staticmethod
    def get_vm_info_by_name(name,tenant_id):
        sql = u"""
                SELECT h.* FROM cmdb_host_logicserver h
                LEFT JOIN mapping_res_tenant_ref r ON r.resource_id = h.id
                WHERE r.resource_type = 'host_logicserver' AND r.tenant_id = :tenant_id
                AND h.name = :name AND h.status <> :status
            """
        os_list = db.session.execute(text(sql), {'name': name,'tenant_id':tenant_id,'status':'destroy'})
        os_list = FormatService.format_result(os_list)
        return os_list

    @staticmethod
    def get_vm_vpn_info(args):
        sql = u"""
                SELECT ip.id,ip.addr FROM cmdb_host_logicserver h LEFT JOIN mapping_host_ip_ref i ON
                i.host_id = h.id LEFT JOIN cmdb_ip ip ON ip.id = i.ip_id WHERE h.internal_id = :internal_id
        """
        result_sql = db.session.execute(sql, {'internal_id': args})
        return result_sql

    @staticmethod
    def check_vm_public_ip(addr):
        sql = u"""
                SELECT * FROM net_internet_ip WHERE source_ip = :source_ip AND removed <> NULL
        """
        result_sql = db.session.execute(sql, {'source_ip': addr})
        return result_sql

    @staticmethod
    def get_vm_list(args):
        args['logicpool_id'] = args['pool_id']
        expung_sql = ''
        if args['recycle'] == 1:
            expung_sql = u"AND h.status in ('expung','deleting') "
        if args['recycle'] == 0:
            expung_sql = u"AND h.status <> 'expung' AND h.status <> 'deleting' AND h.status <> 'destroy'"
        pool_sql = ""
        if args['logicpool_id']:
            pool_sql = u"AND h.logicpool_id = :logicpool_id"
        order_sql = u" ORDER BY h.created DESC"
        sql = u"""
                SELECT distinct h.name,h.status,h.created,h.internal_id,h.trusteeship,
                        h.description AS vm_description,h.id as vm_id,h.removed,h.application_name,
                        h.application_id,ip.addr,tem.os_type,tem.name as template_name,
                        s.name as subnet_name,off.name as offering_name,off.desc,off.cpu,off.mem,off.disksize
                FROM cmdb_host_logicserver h LEFT JOIN mapping_res_tenant_ref t
                ON t.resource_id = h.id LEFT JOIN  mapping_host_ip_ref i ON i.host_id = h.id
                LEFT JOIN mapping_oper_host_ref o ON o.host_id = h.id
                LEFT JOIN cmdb_ip ip ON ip.id = i.ip_id
                LEFT JOIN net_subnet s ON s.segment_id = ip.segment_id
                LEFT JOIN dis_os_template tem ON tem.id = h.os_template_id
                LEFT JOIN dis_offering off ON off.id = h.offeringid
                WHERE t.tenant_id = :tenant_id AND t.resource_type = :resource_type AND h.type='vm'
                AND s.removed is NULL
            """
        if args['keyword']:
            if args['keyword'].has_key('name') and args['keyword']['name']:
                sql1 = """and h.name like '%""" + args['keyword']['name'] + """%'"""
                sql += sql1
            if args['keyword'].has_key('status') and args['keyword']['status']:
                sql2 = """and h.status = '""" + args['keyword']['status'] + """' """
                sql += sql2
            if args['keyword'].has_key('ip') and args['keyword']['ip']:
                sql3 = """and ip.addr like '%""" + args['keyword']['ip'] + """%'"""
                sql += sql3
        limit = u""" limit :start, :per_page"""
        os_list = db.session.execute(text(u''.join([sql,expung_sql,pool_sql,order_sql,limit])),args)
        return os_list

    @staticmethod
    def get_count(tenant_id, resource_type=u'host_logicserver', expung=None, keyword=None,logicpool_id=None):
        pool_sql = ""
        if logicpool_id:
            pool_sql = u"AND h.logicpool_id = :logicpool_id"
        expung_sql = ''
        if expung:
            expung_sql = u"AND h.status in ('expung','deleting') "
        if not expung:
            expung_sql = u"AND h.status <> 'expung' AND h.status <> 'deleting' AND h.status <> 'destroy'"
        try:
            sql = u"""
                   SELECT distinct count(*) AS counts FROM cmdb_host_logicserver h
                   LEFT JOIN mapping_res_tenant_ref t ON t.resource_id = h.id
                   LEFT JOIN  mapping_host_ip_ref i ON i.host_id = h.id
                   LEFT JOIN cmdb_ip ip ON ip.id = i.ip_id
                   WHERE t.tenant_id = :tenant_id AND t.resource_type = :resource_type
                   """
            if keyword:
                if keyword.has_key('name') and keyword['name']:
                    sql1 = """and h.name like '%""" + keyword['name'] + """%'"""
                    sql += sql1
                if keyword.has_key('status') and keyword['status']:
                    sql2 = """and h.status = '""" + keyword['status'] + """' """
                    sql += sql2
                if keyword.has_key('ip') and keyword['ip']:
                    sql3 = """and ip.addr like '%""" + keyword['ip'] + """%'"""
                    sql += sql3
            count = db.session.execute(text(u''.join([sql, expung_sql,pool_sql])),
                                       {'tenant_id': tenant_id, 'resource_type': resource_type,'logicpool_id':logicpool_id})
            for i in count:
                count = i.counts

        except Exception, e:
            print e
        return count

    @staticmethod
    def get_vm_volume(logicserver_id):
        sql = u""" SELECT size AS volume_size,name AS volume_name from cmdb_volume WHERE logicserver_id = :logicserver_id"""
        result_sql = db.session.execute(sql, {'logicserver_id': logicserver_id})
        result_sql = format_result(result_sql)
        if result_sql:
            return result_sql
        else:
            return None

    @staticmethod
    def get_vm_volume_list(logicserver_id):
        sql = u""" SELECT id from cmdb_volume WHERE logicserver_id = :logicserver_id"""
        result_sql = db.session.execute(sql, {'logicserver_id': logicserver_id})
        result_sql = format_result(result_sql)
        if result_sql:
            return result_sql
        else:
            return None

    @staticmethod
    def delete_ref(order_id):
        """
        删除记账表中相关资源
        :param order_id:
        :return:
        """
        sql_delete = u"""
                    DELETE FROM mapping_res_tenant_ref
                    WHERE order_id = :order_id
                    """
        db.session.execute(text(sql_delete), {'order_id': order_id})

    @staticmethod
    def delete_res_allocate(order_id):
        """
        删除记账表中相关资源
        :param order_id:
        :return:
        """
        sql_delete = u"""
                DELETE FROM dis_resource_allocate
                WHERE order_id = :order_id
                """
        db.session.execute(text(sql_delete),{'order_id': order_id})

    @staticmethod
    def delete_vm_by_id(uuid):
        sql_delete = u"""
                    DELETE FROM cmdb_host_logicserver
                    WHERE internal_id = :internal_id
                    """
        db.session.execute(text(sql_delete), {'internal_id': uuid})

    @staticmethod
    def insert_op_mapping(args):
        """

        :param args:
        :return:
        """
        sql = u""" insert into mapping_oper_host_ref(host_id, oper_id, ref_type)
                    VALUES(:host_id, :oper_id, :ref_type) """
        db.session.execute(sql, args)

    @staticmethod
    def insert_bigeye_policy_mapping(args):
        """

        :param args:
        :return:
        """
        sql = u""" insert into opr_host_bigeye_ref(host_id, cluster_id, policy_id, job_id, param)
                      VALUES(:host_id, :cluster_id, :policy_id, :job_id, :param) """
        db.session.execute(sql, args)


    @staticmethod
    def get_os_template_by_id(os_id):
        """

        :param os_id:
        :return:
        """
        sql_select = u"""select DISTINCT ot.* from dis_os_template ot where id = :id
                          """
        os_list = db.session.execute(text(sql_select),{'id':os_id})
        return os_list

    @staticmethod
    def delete_volume(vm_id):
        """

        :param vm_id:
        :return:
        """
        sql_delete = u"""
                    DELETE FROM cmdb_volume WHERE logicserver_id = :logicserver_id
                    """
        db.session.execute(text(sql_delete), {'logicserver_id': vm_id})

    @staticmethod
    def remove_ip_host_ref(vm_id):
        sql_delete = u"""
                    DELETE FROM mapping_host_ip_ref WHERE host_id = :host_id
                    """
        db.session.execute(text(sql_delete), {'host_id': vm_id})
        db.session.commit()

    @staticmethod
    def remove_oper_host_ref(vm_id):
        sql_delete = u"""
                    DELETE FROM mapping_oper_host_ref WHERE host_id = :host_id
                    """
        db.session.execute(text(sql_delete), {'host_id': vm_id})
        db.session.commit()

    @staticmethod
    def remove_bigeye_poicy_host_ref(vm_id):
        sql_delete = u"""
                    DELETE FROM opr_host_bigeye_ref WHERE host_id = :host_id
                    """
        db.session.execute(text(sql_delete), {'host_id': vm_id})
        db.session.commit()

    # 虚机接管方法

    @staticmethod
    def get_cluster_id(cluster_name):
        sql_select = u"""SELECT DISTINCT id FROM inf_vmware_cluster  WHERE name = :name"""
        res = db.session.execute(text(sql_select), {'name': cluster_name})
        if res:
            id_ = format_result(res)[0]
            return id_['id']

    @staticmethod
    def get_offering_id(dict_):
        sql_select = u"""SELECT DISTINCT id FROM dis_offering  WHERE cpu = :cpu AND mem = :mem"""
        res = db.session.execute(text(sql_select), dict_)
        if res:
            id_ = format_result(res)[0]
            return id_['id']

    @staticmethod
    def get_template_id(dict_):
        sql_select = u"""SELECT DISTINCT id FROM dis_os_template  WHERE `desc` = :desc"""
        res = db.session.execute(text(sql_select), dict_)
        if res:
            id_ = format_result(res)[0]
            return id_['id']

    @staticmethod
    def get_logic_pool_id(dict_):
        sql_select = u"""SELECT DISTINCT logic_pool_id FROM inf_pool_cluster_ref  
                          WHERE physic_pool_id = :physic_pool_id"""
        res = db.session.execute(text(sql_select), dict_)
        if res:
            id_ = format_result(res)[0]
            return id_['logic_pool_id']