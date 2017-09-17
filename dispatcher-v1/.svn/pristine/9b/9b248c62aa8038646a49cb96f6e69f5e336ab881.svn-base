# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-12-30
    备份策略与数据库交互模块
"""
from flask import current_app
from sqlalchemy import text

from app.configs.code import ResponseCode
from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result
from app.utils.response import res


class OprBackupPolicy(db.Model, CRUDMixin):
    """备份管理"""
    __tablename__ = 'opr_backup_policy'

    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(16), nullable=False, server_default=text("'VM'"))
    resource_id = db.Column(db.Integer, nullable=False)
    default = db.Column(db.String(4), nullable=False, server_default=text("'YES'"))
    increment = db.Column(db.String(4), nullable=False, server_default=text("'YES'"))
    backup_frequency = db.Column(db.Integer, nullable=False)
    backup_frequency_unit = db.Column(db.String(4), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    backup_path = db.Column(db.String(160), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    name = db.Column(db.String(100), nullable=False)

    @classmethod
    def insert_backup(cls, args):
        """
        添加备份策略
        :param args:
        :return:
        """
        try:
            sql = u""" insert into opr_backup_policy (resource_type, resource_id, `default`, increment, backup_frequency,
                   backup_frequency_unit, period, backup_path, created, `name`, status)
                   VALUES (:resource_type, :resource_id, :default, :increment, :backup_frequency,
                   :backup_frequency_unit, :period, :backup_path, :created, :name, :status)"""
            data = db.session.execute(sql, args)
            id_ = data.lastrowid
            return id_
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @classmethod
    def update_backup(cls, args):
        """ 修改备份策略"""
        try:
            sql = u""" update opr_backup_policy set `default` = :default, increment = :increment, backup_frequency = :backup_frequency,
                    backup_frequency_unit = :backup_frequency_unit, period = :period, backup_path = :backup_path
                    WHERE id = :id"""
            db.session.execute(sql, args)
            data = {'order_id': args['order_id'], 'serial_number': args['serial_number']}
            return res(ResponseCode.SUCCEED, u'修改成功!', None, data)
        except Exception, e:
            current_app.logger.error(u'请求异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @classmethod
    def get_list_by_id(cls, args):
        """根据资源id查看详情"""
        sql = u""" SELECT chl.name, chl.type resource_type,chl.id resource_id, obp.id,obp.`default`,obp.increment,obp.status,
                obp.backup_frequency,obp.backup_frequency_unit,obp.period, obp.backup_path,obp.created,tem.os_type,ci.addr,chl.application_id
                FROM cmdb_host_logicserver chl left JOIN opr_backup_policy obp on chl.id = obp.resource_id
                LEFT JOIN mapping_host_ip_ref mhi on mhi.host_id = chl.id LEFT JOIN cmdb_ip ci on ci.id = mhi.ip_id
                LEFT JOIN dis_os_template tem ON tem.id = chl.os_template_id
                WHERE chl.id = :resource_id AND obp.removed is NULL """
        result = db.session.execute(sql, {'resource_id': args})
        result = format_result(result)
        return result

    @classmethod
    def list_by_condition(cls, args):
        """高级搜索"""
        sql = u""" SELECT chl.name, obp.resource_type,obp.resource_id, obp.id, obp.`default`, obp.increment,chl.application_id,
               tem.os_type,ci.addr,obp.backup_frequency,obp.backup_frequency_unit,obp.period, obp.backup_path,obp.created,obp.status
               FROM cmdb_host_logicserver chl left JOIN opr_backup_policy obp on chl.id = obp.resource_id
        	   LEFT JOIN mapping_host_ip_ref mhi on mhi.host_id = chl.id LEFT JOIN cmdb_ip ci on ci.id = mhi.ip_id
        	   LEFT JOIN dis_os_template tem ON tem.id = chl.os_template_id
               """
        sql_where = OprBackupPolicy.where_sql(args)
        sql_order = u""" ORDER BY obp.id desc limit :start, :per_page"""
        result = db.session.execute(text(u''.join([sql, sql_where, sql_order])), args)
        result = format_result(result)
        return result

    @classmethod
    def get_count_by_condition(cls, args):
        """根据条件查询列表条数"""
        sql = u""" select count(chl.id) as te
                  FROM cmdb_host_logicserver chl left JOIN opr_backup_policy obp on chl.id = obp.resource_id
                  LEFT JOIN mapping_host_ip_ref mhi on mhi.host_id = chl.id LEFT JOIN cmdb_ip ci on ci.id = mhi.ip_id
                  LEFT JOIN dis_os_template tem ON tem.id = chl.os_template_id
                  """
        sql_where = OprBackupPolicy.where_sql(args)
        total_count = db.session.execute(text(u''.join([sql, sql_where])), args)
        for i in total_count:
            itc = i.te
            return itc

    @classmethod
    def get_by_resource_id(cls, args):
        """根据资源id查询数据是否存在"""
        sql = u""" select * from opr_backup_policy where resource_id = :resource_id and removed is NULL """
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def get_resource_list(cls,args):
        """获取没有备份策略的主机"""
        sql = u""" SELECT chl.name, chl.type resource_type,chl.id resource_id,ci.addr,chl.application_id,obp.status,obp.created,
                obp.backup_path FROM cmdb_host_logicserver chl left JOIN opr_backup_policy obp on  obp.resource_id is null
                LEFT JOIN mapping_host_ip_ref mhi on mhi.host_id = chl.id LEFT JOIN cmdb_ip ci on ci.id = mhi.ip_id
                LEFT JOIN dis_os_template tem ON tem.id = chl.os_template_id
                WHERE chl.application_id in :application_id AND ci.addr is not NULL AND
                chl.removed is NULL AND chl.`status` = 'running' and obp.removed is NULL AND tem.os_type NOT LIKE '%Windows%'
                and chl.id not in(select resource_id from opr_backup_policy where removed is null) ORDER BY chl.id"""
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def get_list_restore(cls, args):
        """备份还原下拉列表"""
        sql = u""" SELECT chl.name, chl.type resource_type,chl.id resource_id,ci.addr,chl.application_id,obp.status,obp.created,
                obp.backup_path FROM opr_backup_policy obp  left JOIN cmdb_host_logicserver chl on chl.id = obp.resource_id
				LEFT JOIN mapping_host_ip_ref mhi on mhi.host_id = chl.id LEFT JOIN cmdb_ip ci on ci.id = mhi.ip_id
                WHERE chl.application_id in :application_id AND chl.removed is NULL AND chl.`status` = 'running'
                AND obp.removed is NULL ORDER BY obp.id desc"""
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def where_sql(cls, args):
        """判断where条件并进行拼接"""
        sql_where = u""" WHERE chl.application_id in ({}) AND obp.removed is NULL AND chl.removed is NULL
               AND chl.`status` = 'running' AND obp.id is not NULL
               """.format(args['application_ids'])
        if args['name'] is not None and args['name'] != '':
            args['name'] = u''.join(['%', args['name'], '%'])
            sql_where = u''.join([sql_where, u""" and chl.name like :name"""])
        if args['os_type'] is not None and args['os_type'] != '':
            args['os_type'] = u''.join(['%', args['os_type'], '%'])
            sql_where = u''.join([sql_where, u""" and tem.os_type like :os_type"""])
        if args['status'] is not None and args['status'] != '':
            sql_where = u''.join([sql_where, u""" and obp.status = :status"""])
        if args['default'] is not None and args['default'] != '':
            sql_where = u''.join([sql_where, u""" and obp.default = :default"""])
        return sql_where

    @classmethod
    def list_by_id(cls, args):
        """根据id查看列表"""
        sql = u""" select * from opr_backup_policy where id = :id"""
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result
