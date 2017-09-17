# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gsliu 2017-02-07
    回收站策略与数据库交互
"""
from flask import current_app
from sqlalchemy import text

from app.configs.code import ResponseCode
from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result
from app.utils.response import res


class ComRecyclePolicy(db.Model, CRUDMixin):
    __tablename__ = 'com_recycle_policy'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    object = db.Column(db.String(16), nullable=False, server_default=text("'vm'"))
    status = db.Column(db.Enum(u'disabled', u'enable'), nullable=False, server_default=text("'enable'"))
    recycle_frequency = db.Column(db.Integer, nullable=False, server_default=text("'7'"))
    recycle_frequency_unit = db.Column(db.String(4), nullable=False, server_default=text("'DAY'"))
    recycle_method = db.Column(db.String(10), nullable=False, server_default=text("'NOTIFY'"))
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    tenant_id = db.Column(db.Integer)

    @classmethod
    def get_list(cls, args):
        """根据租户id获取列表"""
        sql = u""" select * from com_recycle_policy WHERE tenant_id = :tenant_id AND removed IS NULL """
        if args['id'] is not None:
            sql = u''.join([sql, u""" and id = :id"""])
        if args['name'] is not None:
            args['name'] = u''.join(['%', args['name'], '%'])
            sql = u''.join([sql, u""" and name like :name"""])
        if args['recycle_frequency'] is not None and args['recycle_frequency_unit'] is not None:
            sql = u''.join([sql, u""" and recycle_frequency = :recycle_frequency and recycle_frequency_unit = :recycle_frequency_unit"""])
        if args['status'] is not None:
            sql = u''.join([sql, u""" and status = :status"""])
        if args['object'] is not None:
            sql = u''.join([sql, u""" and object = :object"""])
        sql = u''.join([sql, u""" order by id limit :start, :per_page"""])
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def get_list_count(cls, args):
        """根据租户id获取列表条数"""
        sql = u""" select count(id) as te from com_recycle_policy WHERE tenant_id = :tenant_id AND removed IS NULL """
        if args['id'] is not None:
            sql = u''.join([sql, u""" and id = :id"""])
        if args['name'] is not None:
            args['name'] = u''.join(['%', args['name'], '%'])
            sql = u''.join([sql, u""" and name like :name"""])
        if args['recycle_frequency'] is not None and args['recycle_frequency_unit'] is not None:
            sql = u''.join([sql, u""" and recycle_frequency = :recycle_frequency and recycle_frequency_unit = :recycle_frequency_unit"""])
        if args['status'] is not None:
            sql = u''.join([sql, u""" and status = :status"""])
        if args['object'] is not None:
            sql = u''.join([sql, u""" and object = :object"""])
        total_count = db.session.execute(sql, args)
        for i in total_count:
            itc = i.te
            return itc

    @classmethod
    def insert_recycle_policy(cls, args):
        """添加回收站策略"""
        try:
            sql = u""" insert into com_recycle_policy(`name`, description, object, status, recycle_frequency,
                      recycle_frequency_unit, recycle_method, created, tenant_id)
                      VALUES (:name, :description, :objects, :status, :recycle_frequency, :recycle_frequency_unit,
                      :recycle_method, :created, :tenant_id)"""
            data = db.session.execute(sql, args)
            id_ = data.lastrowid
            return id_
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @classmethod
    def get_object(cls, args):
        """查询租户已经添加的策略对象"""
        sql = u""" select * from com_recycle_policy WHERE tenant_id = :tenant_id AND removed IS NULL """
        result = db.session.execute(sql, args)
        return result

    @classmethod
    def update_removed(cls, args):
        """将回收策略删除"""
        try:
            sql = u""" UPDATE com_recycle_policy SET removed = :removed WHERE id IN :id """
            db.session.execute(sql, args)
            return res(ResponseCode.SUCCEED, u'删除成功！')
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @classmethod
    def update_status(cls, args):
        """修改回收站策略状态"""
        try:
            sql = u""" UPDATE com_recycle_policy SET status = :status WHERE id IN :id """
            db.session.execute(sql, args)
            return res(ResponseCode.SUCCEED, u'修改成功！')
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @classmethod
    def update_policy(cls, args):
        """修改回收站策略"""
        try:
            sql = u""" UPDATE com_recycle_policy SET status = :status , `name` = :name , description = :description,
                      recycle_method = :recycle_method , recycle_frequency = :recycle_frequency ,
                      recycle_frequency_unit = :recycle_frequency_unit WHERE id = :id """
            db.session.execute(sql, args)
            return res(ResponseCode.SUCCEED, u'修改成功！')
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return res(ResponseCode.ERROR, e)

    @classmethod
    def get_by_id(cls, id_):
        """根据id查询"""
        sql = u""" select * from com_recycle_policy WHERE  id = :id_"""
        result = db.session.execute(sql, {'id_': id_})
        result = format_result(result)
        return result


