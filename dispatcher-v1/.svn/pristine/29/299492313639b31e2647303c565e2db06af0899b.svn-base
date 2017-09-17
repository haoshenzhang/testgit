# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    app.utils.async
    daiguanlin 2016-11-25
"""

from app.extensions import db
from app.utils.database import CRUDMixin
from sqlalchemy import text
from app.utils import helpers
from app.utils.format import FormatService


class ComAsyncTask(db.Model, CRUDMixin):
    __tablename__ = 'com_async_task'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    result = db.Column(db.Text, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def insert_new_task(order_id, user_id, tenant_id, task_item_id, system_type):
        now = helpers.str_now()
        sql_insert = u"""
        INSERT INTO com_async_task (`order_id`, `user_id`, `tenant_id`, `name`,`system_type`,`status`,`created`)
        VALUES (:order_id, :user_id, :tenant_id, :name, :system_type, :status, :created)
        """
        res = db.session.execute(text(sql_insert),
                           {'order_id': order_id, 'user_id': user_id, 'tenant_id': tenant_id,
                            'name': task_item_id, 'system_type': system_type, 'status': u'STARTING','created':now
                            })
        db.session.commit()
        return res.lastrowid

    @staticmethod
    def get_async_task_status(order_id, task_id):
        sql = u"""
            SELECT * FROM com_async_task WHERE order_id= :order_id AND id= :id
        """
        # wfluo 20170425 处理缓存问题
        # db.session.flush()
        res = db.session.execute(text(sql), {'order_id': order_id, 'id': task_id})
        res = FormatService.format_result(res)
        if res:
            return res[0]
        else:
            return None

    @staticmethod
    def get_async_task(order_id):
        sql = u"""
            SELECT * FROM com_async_task WHERE order_id= :order_id
        """
        # wfluo 20170425 处理缓存问题
        db.session.flush()
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = FormatService.format_result(res)
        return res

    @staticmethod
    def update_async_task_status(task_id, status, code):
        sql = u"""
                update com_async_task a set a.status=:status,a.code=:code
                where a.id = :id
        """

        res = db.session.execute(text(sql), {'id': task_id, 'status': status, 'code': code})
        db.session.commit()
        return res

    @staticmethod
    def update_async_task(task_id, status, code,result):
        try:
            sql = u"""
                    update com_async_task a set a.status=:status,a.code=:code,a.result=:result
                    where a.id = :id
            """

            res = db.session.execute(text(sql), {'id': task_id, 'status': status, 'code': code, 'result':result})
            db.session.commit()
            return res
        except Exception, e:
            print e

    @staticmethod
    def del_com_task(id):
        sql_delete = u"""
                    DELETE from com_async_task
                    WHERE id = :id
                    """
        db.session.execute(text(sql_delete),
                           {'id': id})
        db.session.commit()

    @staticmethod
    def app_context_flush():
        """wfluo 2017-04-26 针对apscheduler调试，数据库进行flush操作"""
        db.session.flush()


class CmdbIpSegment(object):

    @staticmethod
    def get_vlan_id(id):
        try:
            sql = u"""
                    SELECT vlan_id FROM cmdb_ip_segment WHERE id = :id
            """
            res = db.session.execute(text(sql), {'id': id})
            res = FormatService.format_result(res)[0]['vlan_id']
            return res
        except Exception as e:
            print e

    @staticmethod
    def get_ip_segment_by(id,field):
        sql = u"""
            SELECT * FROM cmdb_ip_segment WHERE id = :id
        """
        res = db.session.execute(text(sql), {'id': id})
        res = FormatService.format_result(res)[0]
        return res[field]
