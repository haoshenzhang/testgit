# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2016-11-25
    安全服务与数据库交互模块
"""
from sqlalchemy import text
from flask import current_app

from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result


class NetTenantSecurityservicesRef(db.Model, CRUDMixin):
    __tablename__ = 'net_tenant_securityservices_ref'

    id = db.Column(db.Integer, primary_key=True)
    security_services_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    unit = db.Column(db.String(20))
    created = db.Column(db.DateTime)
    removed = db.Column(db.DateTime)

    @classmethod
    def get_list_by_id(cls, args):
        """根据id查询安全服务项"""
        sql = u""" select nts.id, nts.security_services_id, nts.tenant_id, nts.period,
            DATE_FORMAT(nts.start_date,'%Y-%m-%d') start_date, DATE_FORMAT(nts.end_date,'%Y-%m-%d') end_date,
            nts.created, nts.removed, cs.name, cs.description, cs.status, nts.unit, cs.remark, nts.number
            from net_tenant_securityservices_ref nts inner join cmdb_security_services cs
            on nts.security_services_id = cs.id where nts.removed is null and nts.id = :id """
        security_list = db.session.execute(sql, args)
        return security_list

    @classmethod
    def list_by_tenant(cls, args):
        """根据租户id查询安全服务项"""
        sql = u""" select nts.id, nts.security_services_id, nts.tenant_id, nts.period,
            DATE_FORMAT(nts.start_date,'%Y-%m-%d') start_date, DATE_FORMAT(nts.end_date,'%Y-%m-%d') end_date,
            nts.created, nts.removed, cs.name, cs.description, cs.status, nts.unit, cs.remark, nts.number
            from net_tenant_securityservices_ref nts inner join cmdb_security_services cs
            on nts.security_services_id = cs.id where nts.removed is null and nts.tenant_id = :tenant_id order by nts.id"""
        security_list = db.session.execute(sql, args)
        return security_list

    @classmethod
    def insert_security_tenant(cls, args):
        """关联租户与安全服务项"""
        try:
            sql = u""" insert into net_tenant_securityservices_ref(security_services_id, tenant_id, created)
                  VALUES(:security_servicesid, :tenant_id, :created)"""
            data = db.session.execute(sql, args)
            id_ = data.lastrowid
            return id_
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)

    @classmethod
    def update_security(cls, args):
        """根据id修改关联表"""
        sql = u""" update net_tenant_securityservices_ref set number = :number, unit = :unit, start_date = :start_date,
                   end_date = :end_date, period = FLOOR(DATEDIFF(:end_date,:start_date)/365) WHERE id = :id"""
        db.session.execute(sql, args)

    @classmethod
    def get_security_list(cls):
        """查询所有安全服务"""
        sql = u""" select * from cmdb_security_services"""
        result_sql = db.session.execute(sql)
        result_sql = format_result(result_sql)
        return result_sql

    @classmethod
    def get_list_by_tenant_and_security(cls, args):
        """根据租户id和安全服务项id查询"""
        sql = u""" select * from net_tenant_securityservices_ref WHERE tenant_id = :tenant_id
                AND security_services_id = :security_servicesid AND removed is null"""
        result_sql = db.session.execute(sql, args)
        result_sql = format_result(result_sql)
        return result_sql


