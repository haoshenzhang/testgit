# !/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from app.catalog.public_ip.constant import IpStatus
from app.extensions import db
from app.order.constant import ResourceType
from app.utils.database import CRUDMixin
from app.utils.format import format_result


class PhysicalCluster(CRUDMixin):


    @classmethod
    def get_list(cls, args):
        data = None
        try:
            sql = u"""
                   select a.* from cmdb_pm_cluster a,mapping_res_tenant_ref b where
                    a.logicpool_id = :logicpool_id and  b.tenant_id=:tenant_id and a.id=b.resource_id and a.removed is NULL
                   and b.resource_type= '"""+ResourceType.PM_Cluster.value+"'"
            if args['keyword']:
                if args['keyword'].has_key('name') and args['keyword']['name']:
                    sql1 = """and a.name like '%"""+args['keyword']['name']+"""%'"""
                    sql += sql1
                if args['keyword'].has_key('status') and args['keyword']['status']:
                    sql2 = """and a.status like '%"""+args['keyword']['status']+"""%'"""
                    sql +=sql2
            limit = u""" order by a.created desc limit :start, :per_page"""
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(u''.join([sql, limit])), args)
        except Exception, e:
            print e

        return data

    @classmethod
    def get_order_data(cls, args):
        data = None
        try:
            sql = u"""
                   select d.serial_number,d.operation_type from dis_mapping_res_order c,dis_order d  where
                    c.order_id = d.id and c.resource_id=:id and c.resource_type= '"""+ResourceType.PM_Cluster.value+"'"+\
                "group by d.created desc"

            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), {'id':args})
        except Exception, e:
            print e

        return data

    @classmethod
    def get_count(cls, args):
        data = None
        try:
            sql = u"""
                   select count(*) as counts from cmdb_pm_cluster a,mapping_res_tenant_ref b  where
                    a.logicpool_id = :logicpool_id and  b.tenant_id=:tenant_id and a.id=b.resource_id and a.removed is NULL
                    and b.resource_type= '"""+ResourceType.PM_Cluster.value+"'"
            if args['keyword']:
                if args['keyword'].has_key('name') and args['keyword']['name']:
                    sql1 = """and a.name like '%"""+args['keyword']['name']+"""%'"""
                    sql += sql1
                if args['keyword'].has_key('status') and args['keyword']['status']:
                    sql2 = """and a.status like '%"""+args['keyword']['status']+"""%'"""
                    sql +=sql2
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            count = db.session.execute(text(sql), args)
            for i in count:
                count = i.counts
        except Exception, e:
            print e

        return count

    @classmethod
    def create_pm_cluster(cls, args):
        # 创建磁盘组
        data = None
        try:
            sql = u"""
                insert into cmdb_pm_cluster(application_name, name, description, created, application_id, logicpool_id, status, trusteeship)
                values(:application_name, :name, :description, :created, :application_id, :logicpool_id, :status, :trusteeship)
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            id = data.lastrowid
            db.session.commit()
            print id
        except Exception, e:
            print e

        return id

    @classmethod
    def update_pm_cluster(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_pm_cluster a set a.name=:name , a.description = :description
                where a.id = :id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            id = data.lastrowid
            print id
        except Exception, e:
            print e

        return id


    @classmethod
    def list_volume_group(cls, args):
        data = None
        try:
            sql = u"""
                select * from cmdb_pm_cluster a
                limit :start, :perpage
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            id = data.lastrowid
            print id
        except Exception, e:
            print e

        return id

    @classmethod
    def check_name(cls, args):
        data = None
        try:
            sql = u"""
                select * from cmdb_pm_cluster a where a.name =:name
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

        return data

    @classmethod
    def update_pm_cluster_status(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_pm_cluster a set a.status=:status
                where a.id = :id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e


class pm():
    # 物理机
    @classmethod
    def get_pm_by_orderid_resourcetype(cls,order_id,resource_type):
        # 通过orderid和resourcetyoe获取物理机信息
        try:
            sql = u"""
                    SELECT b.*  FROM dis_mapping_res_order a,cmdb_host_logicserver b
                    where a.order_id = :order_id and a.resource_type = :resource_type and a.resource_id = b.id
                             """
            data_list = db.session.execute(text(sql), {'order_id': order_id, 'resource_type': resource_type})

            db.session.commit()
        except Exception, e:
            print e

        return data_list

    @classmethod
    def delete_resource_allocate_by_orderid_type(cls, args):
        # 修改remove字段
        try:
            sql_update = u"""update dis_resource_allocate set removed = :removed
                        where order_id = :order_id and allocate_type =:allocate_type
                                """
            db.session.execute(text(sql_update), args)

            db.session.commit()
        except Exception, e:
            print e

    @classmethod
    def update_ip_status(cls, args):
        # 修改ip状态
        try:
            status = IpStatus.using
            sql_update = u"""update cmdb_ip set status = :status where id = :id
                                """
            db.session.execute(text(sql_update), args)

            db.session.commit()
        except Exception, e:
            print e

    @classmethod
    def update_allocate_ip_status(cls, args):
        # 删除记账表
        try:
            status = IpStatus.using
            sql_update = u"""update cmdb_ip set status = :status where id = :id
                                """
            db.session.execute(text(sql_update), args)

            db.session.commit()
        except Exception, e:
            print e

    @classmethod
    def check_name(cls, args):
        data = None
        try:
            sql = u"""
                select * from cmdb_host_logicserver a where a.name =:name and a.type = 'pm' and a.application_id in :applicationidList
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

        return data

    @classmethod
    def create_pm(cls, args):
        # 创建物理机
        data = None
        try:
            sql = u"""
                insert into cmdb_host_logicserver(application_id,application_name, name, cpu, mem,type, logicpool_id, created, description, status, offeringid, trusteeship, host_name, pm_cluster_id, os_template_id)
                values(:application_id, :application_name, :name, :cpu, :mem,:type, :logicpool_id, :created, :description, :status, :offeringid, :trusteeship, :host_name, :pm_cluster_id, :os_template_id)
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            id = data.lastrowid
            db.session.commit()
            print id
        except Exception, e:
            print e

        return id

    @classmethod
    def insert_mapping_host_ip(cls, args):
        # ip关联资源
        data = None
        try:
            sql = u"""
                insert into mapping_host_ip_ref(host_id, ip_id, ref_type)
                values(:host_id, :ip_id, :ref_type)
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e


    @classmethod
    def get_list(cls,args):
        data = None
        try:
            sql = u"""
               select a.* ,b.name,b.desc,b.cpu as offeringcpu, b.mem as offeringmem,b.disksize, d.addr,d.location,d.segment_id, e.name as template_name,e.os_type
               from cmdb_host_logicserver a ,dis_offering b ,mapping_host_ip_ref c, cmdb_ip d, dis_os_template e
               where a.pm_cluster_id =:pm_cluster_id and a.offeringid=b.id and a.id=c.host_id and c.ip_id=d.id
               and e.id = a.os_template_id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            result_sql = format_result(data)
        except Exception, e:
            print e

        return result_sql

    @classmethod
    def get_list_page(cls,args):
        data = None
        try:
            sql = u"""
               select a.* ,b.name as offeringname,b.desc,b.cpu as offeringcpu, b.mem as offeringmem,b.disksize, d.addr,d.location,d.segment_id,g.serial_number,
               h.name as template_name, h.os_type
               from cmdb_host_logicserver a ,dis_offering b ,mapping_host_ip_ref c, cmdb_ip d,mapping_res_tenant_ref e
               ,dis_mapping_res_order f, dis_order g, dis_os_template h
               where f.order_id = g.id and f.resource_id=a.id and h.id = a.os_template_id and f.resource_type= '"""+ResourceType.PM.value+"'"+\
               """ and a.pm_cluster_id is null and a.offeringid=b.id and a.id=c.host_id and c.ip_id=d.id
               and a.logicpool_id = :logicpool_id and  e.tenant_id=:tenant_id and a.id=e.resource_id and a.removed is NULL
               and e.resource_type='"""+ResourceType.PM.value+"'"

            if args['keyword']:
                if args['keyword'].has_key('name') and args['keyword']['name']:
                    sql1 = """and a.name like '%"""+args['keyword']['name']+"""%'"""
                    sql += sql1
                if args['keyword'].has_key('status') and args['keyword']['status']:
                    sql2 = """and a.status like '%"""+args['keyword']['status']+"""%'"""
                    sql +=sql2
                if args['keyword'].has_key('addr') and args['keyword']['addr']:
                    sql3 = """and d.addr like '%"""+args['keyword']['addr']+"""%'"""
                    sql +=sql3
            limit = u"""order by a.created desc limit :start, :per_page"""

            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(u''.join([sql, limit])), args)
            result_sql = format_result(data)
        except Exception, e:
            print e

        return result_sql

    @classmethod
    def get_count(cls, args):
        data = None
        try:
            sql = u"""
                   select count(*) as counts
               from cmdb_host_logicserver a ,dis_offering b ,mapping_host_ip_ref c, cmdb_ip d,mapping_res_tenant_ref e
               where a.pm_cluster_id is null and a.offeringid=b.id and a.id=c.host_id and c.ip_id=d.id
               and a.logicpool_id = :logicpool_id and  e.tenant_id=:tenant_id and a.id=e.resource_id and a.removed is NULL
               and e.resource_type='"""+ResourceType.PM.value+"'"
            if args['keyword']:
                if args['keyword'].has_key('name') and args['keyword']['name']:
                    sql1 = """and a.name like '%"""+args['keyword']['name']+"""%'"""
                    sql += sql1
                if args['keyword'].has_key('status') and args['keyword']['status']:
                    sql2 = """and a.status like '%"""+args['keyword']['status']+"""%'"""
                    sql +=sql2
                if args['keyword'].has_key('addr') and args['keyword']['addr']:
                    sql3 = """and d.addr like '%"""+args['keyword']['addr']+"""%'"""
                    sql +=sql3
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            count = db.session.execute(text(sql), args)
            for i in count:
                count = i.counts
        except Exception, e:
            print e

        return count

    @classmethod
    def get_subnet_list(cls,args):
        #查询子网
        data = None
        try:
            sql = u"""
                select a.name from net_subnet a where segment_id = :segment_id and a.status!='expunge' and a.removed is null
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            result_sql = format_result(data)
        except Exception, e:
            print e

        return result_sql

    @classmethod
    def get_subnet_list_all(cls,args):
        #查询子网
        data = None
        try:
            sql = u"""
                select * from net_subnet
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            result_sql = format_result(data)
        except Exception, e:
            print e

        return result_sql

    @classmethod
    def update_pm_status(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_host_logicserver a set a.status=:status
                where a.id = :id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

    @classmethod
    def update_pm(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_host_logicserver a set a.name=:name,a.description=:description
                where a.id = :id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

    @classmethod
    def update_pm_coss_id(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_host_logicserver a set a.coss_id=:coss_id
                where a.host_name = :host_name
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

class overview():
    #概览展示
    @classmethod
    def get_server_count_by_mtype(cls,args):
        sql1 = ''
        try:
            sql = u"""
                select count(*) from cmdb_host_logicserver a where a.type=:type and a.applicationid in :applicationidList
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e

    @classmethod
    def get_server_count_by_ostype_mtype(cls,args):
        data = None
        try:
            sql = u"""
                select count(*) from cmdb_host_logicserver a,dis_os_template b where a.type=:m_type and a.application_id in :applicationidList and a.removed IS NULL
                and a.os_template_id = b.id and b.os_type like :os_type and a.status !='destroy'
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e
        return data
    @classmethod
    def get_server_count_by_configid_mtype(cls,args):
        data = None
        try:
            sql = u"""
                select count(*) from cmdb_host_logicserver a where a.type=:m_type and a.application_id in :applicationidList and a.removed IS NULL
                and a.offeringid = :offeringid and a.status !='destroy'
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e
        return data

    @classmethod
    def get_server_count_by_status_mtype(cls,args):
        data = None
        sql1 = ''
        try:
            sql = u"""
                select count(1) as count,a.status from cmdb_host_logicserver a
                where a.type=:m_type and a.application_id in :applicationidList  and a.removed IS NULL and a.status !='destroy'
                GROUP BY a.status
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e
        return data

    @classmethod
    def get_offering_by_mtype(cls,args):
        data = None
        try:
            sql = u"""
                select * from dis_offering a where a.type=:m_type
                """
            data = db.session.execute(text(sql), args)
        except Exception, e:
            print e
        return data