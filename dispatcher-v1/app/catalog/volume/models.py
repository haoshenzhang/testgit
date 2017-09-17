# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-28
    与数据库交互
"""
from sqlalchemy import text
from flask import current_app

from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result


class CmdbVolume(db.Model, CRUDMixin):
    __tablename__ = 'cmdb_volume'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    application_id = db.Column(db.Integer, nullable=False)
    logicpool_id = db.Column(db.Integer, nullable=False)
    physic_pool_id = db.Column(db.Integer)
    logicserver_id = db.Column(db.Integer)
    groupvolume_id = db.Column(db.Integer)
    description = db.Column(db.String(256))
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def get(cls, args):
        """根据id查询虚机卷"""
        sql_select = u""" select cv.id, cv.name, cv.size, cv.type, cv.status, cv.application_id, cv.logicpool_id,
            cv.physic_pool_id, cv.logicserver_id, cv.pm_cluster_id, cv.description, cv.created,
            cv.removed, chl.name vm_name"""
        sql_from = u"""  from cmdb_volume cv inner join cmdb_host_logicserver chl
            on cv.logicserver_id = chl.id """
        sql_where = u""" where cv.id = :id """
        volume_list = db.session.execute(text(u''.join([sql_select, sql_from, sql_where])), args)
        return volume_list if volume_list else None

    @classmethod
    def get_by_logicserver_id(cls, args):
        """根据虚机id查询卷列表"""
        sql = u""" select name, size from cmdb_volume where logicserver_id = :logicserver_id and removed is null """
        if args['flag']:
            sql = u''.join([sql, u""" and status = 'expunge'"""])
        else:
            sql = u''.join([sql, u""" and status != 'expunge'"""])
        result_list = db.session.execute(sql, args)
        result_list = format_result(result_list)
        return result_list

    @classmethod
    def insert_volume(cls, args):
        """创建虚机卷"""
        if 'physic_pool_id' not in args.keys():
            args['physic_pool_id'] = None
        if 'logicserver_id' not in args.keys():
            args['logicserver_id'] = None
        if 'description' not in args.keys():
            args['description'] = None
        if 'pm_cluster_id' not in args.keys():
            args['pm_cluster_id'] = None
        if 'hypervisor_type' not in args.keys():
            args['hypervisor_type'] = None
        if 'internal_id' not in args.keys():
            args['internal_id'] = None
        try:
            sql = u"""
                    insert into cmdb_volume(name, size, type, status, application_id, logicpool_id, physic_pool_id,
                    logicserver_id, pm_cluster_id, description, created, hypervisor_type, internal_id)
                    values(:names, :sizes, :type, :status, :application_id, :logicpool_id, :physic_pool_id,
                    :logicserver_id, :pm_cluster_id, :description, :created, :hypervisor_type, :internal_id)
                    """
            data = db.session.execute(sql, args)
            id_ = data.lastrowid
            return id_
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @classmethod
    def update_removed(cls, args):
        """将卷删除，更新removed时间"""
        sql = u""" update cmdb_volume set removed = :removed WHERE logicserver_id = :logicserver_id
                  AND status = 'expunge'"""
        db.session.execute(sql, args)

    @classmethod
    def update_status(cls, args):
        """将卷删除"""
        sql = u""" update cmdb_volume set status = :status WHERE logicserver_id = :logicserver_id"""
        db.session.execute(text(sql), args)

    @classmethod
    def get_volume_back(cls, args):
        """将卷从回收站中还原"""
        sql = u""" update cmdb_volume set status = :status WHERE logicserver_id = :logicserver_id
                  and removed is NULL AND status = 'expunge'"""
        db.session.execute(sql, args)

    @classmethod
    def get_size(cls, args):
        """查询物理机和虚机扩容的和"""
        sql = u""" SELECT sum(size) AS size,cv.type FROM `cmdb_volume` cv   WHERE cv.removed IS NULL
                  AND cv.application_id IN :application_id GROUP BY cv.type"""
        result_sql = db.session.execute(sql, args)
        return result_sql

    @classmethod
    def get_list_by_pmclusterid(cls, args):
        """
        根据集群id查询卷列表
        :param args:
        :return:
        """
        sql = u""" select * from cmdb_volume WHERE pm_cluster_id = :pm_cluster_id"""
        result_sql = db.session.execute(sql, {'pm_cluster_id': args})
        result_sql = format_result(result_sql)
        return result_sql


class CreateVolumeMethod(CRUDMixin):
    @classmethod
    def get_logicserver(cls, args):
        """根据虚机id查询虚机信息"""
        sql = u""" select * from cmdb_host_logicserver where id = :id AND removed is NULL """
        result_sql = db.session.execute(sql, {'id': args})
        result_sql = format_result(result_sql)
        return result_sql

    @classmethod
    def insert_mapping_ref(cls, args):
        """ 创建卷时向租户关系表中插入数据"""
        sql = u""" insert into mapping_res_tenant_ref(tenant_id, resource_type, resource_id, created)
                  VALUES(:tenant_id, :resource_type, :resource_id, :created) """
        db.session.execute(sql, args)

    @classmethod
    def get_logic_pool_detail(cls, args):
        """
        获取客户资源池信息
        :param args:客户资源池id
        :return:
        """
        sql = u""" select * from inf_logic_pool where id = :id"""
        result_sql = db.session.execute(sql, {'id': args})
        result_sql = format_result(result_sql)
        return result_sql

