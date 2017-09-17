# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    订单模型层
"""
import random
from itertools import izip

from flask import current_app
from flask import g
from flask import json

from app.extensions import db
from app.order.constant import OrderStatus, ResourceType
from app.utils.database import CRUDMixin
from sqlalchemy import text
import datetime
import time


class DisOrder(db.Model, CRUDMixin):
    """
    订单信息列表
    """
    __tablename__ = 'dis_order'

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(10), nullable=False)
    application_id = db.Column(db.Integer, nullable=False)
    resource_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    tenant_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    apply_info = db.Column(db.Text)
    created = db.Column(db.Date, nullable=False)
    removed = db.Column(db.DateTime)
    operation_type = db.Column(db.String(30), nullable=False)

    @classmethod
    def get_order_condition_count(cls, args):
        """
        按条件查询资源池数目
        :return:
        """
        sql_select = u"""SELECT count(*) as counts FROM dis_order o """
        sql_where = DisOrder.sql_where(args)
        total_count = db.session.execute(text(u''.join([sql_select, sql_where])), args)
        for i in total_count:
            count = i.counts
        return count

    @classmethod
    def get_order_list_by_args(cls, args):
        """
        功能：按条件查询
        """
        sql = u"""
                  SELECT o.* , u.real_name as user_name FROM dis_order o LEFT JOIN u_user u on o.user_id = u.id """
        sql_where = DisOrder.sql_where(args)
        sql_limit = u""" limit :start, :per_page"""
        data_list = db.session.execute(text(u''.join([sql, sql_where, u""" order by o.created DESC  """, sql_limit])), args)
        return data_list

    @classmethod
    def sql_where(cls, args):
        """
        判断where条件并进行拼接
        :param args:
        :return:
        """
        sql_where = u""" where o.removed is null  """
        if 'tenant_id' in args and  not args['tenant_id']:
            sql_where = u''.join([sql_where, u""" and 1=1"""])
        if 'tenant_id' in args and args['tenant_id']:
            sql_where = u''.join([sql_where, u""" and o.tenant_id=:tenant_id"""])
        if 'user_id' in args and args['user_id']:
            sql_where = u''.join([sql_where, u""" and o.user_id=:user_id"""])
        if args['keyword'].has_key('serial_number') and args['keyword']['serial_number']:
            sql_where = u''.join([sql_where, u""" and o.serial_number like :serial_number""" ])
        if args['keyword'].has_key('status') and args['keyword']['status']:
            sql_where = u''.join([sql_where, u""" and o.status = :status"""])
        if args['keyword'].has_key('application_name') and args['keyword']['application_name']:
            sql_where = u''.join([sql_where, u""" and o.application_name like :application_name"""])
        if args['keyword'].has_key('resource_type') and args['keyword']['resource_type']:
            sql_where = u''.join([sql_where, u""" and o.resource_type = :resource_type"""])
        if args['keyword'].has_key('starttime') and args['keyword']['starttime'] and args['keyword'].has_key('endtime') and args['keyword']['endtime']:
            sql_where = u''.join([sql_where, u""" and o.created between :starttime and :endtime"""])
        return sql_where

    @classmethod
    def get_order_details(cls, order_id):
        """
        wei lai 2016/12/14
        功能：订单详情 （根据order_id）
        """
        sql = u"""
                      SELECT o.*  FROM dis_order o  where o.id = :order_id
                      """
        data_list = db.session.execute(text(sql), {'order_id': order_id})
        return data_list

    @classmethod
    def update_order_status(cls, order_id, status, ticket_id):
        """
        wei lai 2016/12/14
        功能：更新order状态(根据订单ID)
        """

        sql = u"""
                                  UPDATE dis_order  SET status =:status, ticket_id = :ticket_id WHERE id = :order_id
                            """
        db.session.execute(text(sql), {'order_id': order_id, 'status': status, 'ticket_id': ticket_id})

    @classmethod
    def update_only_status(cls,order_id, status):
        """
        只更新订单状态
        :param order_id:
        :param status:
        :return:
        """

        sql = u"""
                                  UPDATE dis_order  SET status =:status WHERE id = :order_id
                            """
        db.session.execute(text(sql), {'order_id': order_id, 'status': status})

    @classmethod
    def update_order_ticket(cls, order_id, ticket_id):
        """
        wei lai 2016/12/14
        功能：更新orderz中的工单id(根据订单ID)
        """
        sql = u"""
                             UPDATE dis_order  SET  ticket_id = :ticket_id WHERE id = :order_id
                       """
        db.session.execute(text(sql), {'order_id': order_id, 'ticket_id': ticket_id})
        db.session.commit

    @classmethod
    def update_status(cls, order_id, status):
        """
        wei lai 2016/12/14
        功能：更新order状态(根据订单ID)
        """
        app_token = g.app_token
        sql = u"""
                              UPDATE dis_order  SET status =:status ,app_token = :app_token WHERE id = :order_id
                        """
        db.session.execute(text(sql), {'order_id': order_id, 'status': status, 'app_token':app_token})

    @classmethod
    def update_apply_info(cls, order_id, apply_info):
        """
        wei lai 2016/12/21
        功能：更新apply_info(根据订单ID),可以将apply_info从新封装
        """
        apply_info = json.dumps(apply_info)
        sql = u""" UPDATE dis_order  SET apply_info =:apply_info WHERE id = :order_id """
        db.session.execute(text(sql), {'order_id': order_id, 'apply_info': apply_info})

    @classmethod
    def created_order(cls, args):
        """
        wei lai 2016/12/14
        功能：创建订单
        """
        application_id = None
        if args.get("application_id"):
            application_id = args["application_id"]
        application_name = None
        if args.get("application_name"):
            application_name = args["application_name"]
        resource_type = args['resource_type']
        user_id = args['user_id']
        tenant_id = args['tenant_id']
        apply_info = args['apply_info']
        operation_type = args['operation_type']
        serial_number = DisOrder.generator_id()
        status = OrderStatus.doing
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        apply_info = json.dumps(apply_info)
        app_token = g.app_token
        sql_insert = u"""INSERT INTO dis_order(application_id,`resource_type`,`operation_type`,`user_id`,`tenant_id`,
                           `status`,`apply_info`,`serial_number`,`created`,application_name, app_token)
                          VALUES (:application_id,:resource_type,:operation_type,:user_id,:tenant_id,:status,:apply_info,
                          :serial_number,:created,:application_name, :app_token)
                      """
        result = db.session.execute(text(sql_insert), {'serial_number': serial_number, 'application_id': application_id,
                                                       'resource_type': resource_type, 'operation_type': operation_type,
                                                       'user_id': user_id, 'tenant_id': tenant_id, 'status': status,
                                                       'apply_info': apply_info, 'created': created, 'application_name':application_name,
                                                       'app_token': app_token})
        order_id = result.lastrowid
        return order_id, serial_number

    @staticmethod
    def generator_id():
        """
        wei lai 2016/12/14
        功能：生成订单号
        """
        # 生成当前时间的时间戳（13位）毫秒级
        millis = int(round(time.time() * 1000))
        t = str(millis)
        # 生成四位随机码
        a = chr(random.randint(97, 122))
        b = str(random.randint(10, 99))
        c = chr(random.randint(97, 122))
        return a+b+t+c

    @staticmethod
    def insert_order_ref(args):
        """
        增加订单和资源关联关系
        :param args: {order_id：订单id；resource_type：资源类型；resource_id：资源id}
        :return:
        """
        try:
            sql = u""" insert into dis_mapping_res_order(order_id, resource_type, resource_id)
                                       VALUES(:order_id, :resource_type, :resource_id) """
            db.session.execute(sql, args)
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @staticmethod
    def insert_order_ref_batch(order_id, resource_types, resource_ids):
        """
        增加订单和资源关联关系
        :param order_id: 订单id
        :param resource_types:资源类型(多個)
        :param resource_ids:资源id(多個)
        :return:
        """

        try:
            sql_values = []
            for resource_type, resource_id in izip(resource_types, resource_ids):
                sql_values.append("({}, {}, {})".format(order_id, resource_type, resource_id))
            sql = "insert into dis_mapping_res_order(`order_id`, `resource_type`, `resource_id`) values {}".format(
                ",".join(sql_values))
            db.session.execute(sql, {'order_id': order_id, 'resource_types': resource_types,'resource_ids': resource_ids})
            db.session.commit()
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @classmethod
    def get_resource_by_order(cls, order_id, resource_type):
        """
        wei lai 2016/12/14
        根据订单id，资源类型查询资源id
        :param order_id: 资源id
        :param resource_type: 资源类型
        """
        sql = u"""
                SELECT *  FROM dis_mapping_res_order where order_id = :order_id and resource_type = :resource_type
                         """
        data_list = db.session.execute(text(sql), {'order_id': order_id, 'resource_type': resource_type})
        return data_list


class DisOrderLog(db.Model, CRUDMixin):
    """
    订单日志数据表
    """
    __tablename__ = 'dis_order_log'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    order_id = db.Column(db.Integer,  nullable=False)
    status = db.Column(db.String(20),  nullable=False)
    log_info = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)

    @classmethod
    def created_order_log(cls, args):
        """
        wei lai 2016/12/14
        功能：创建订单日志
        """
        try:
            order_id = args['order_id']
            operation_object = args['operation_object']
            operation_name = args['operation_name']
            execution_status = args['execution_status']
            now = datetime.datetime.now()
            created = now.strftime("%Y-%m-%d %H:%M:%S")
            sql_insert = u"""INSERT INTO dis_order_log(execution_status,`operation_name`,`order_id`,`created`,`operation_object`)
                             VALUES (:execution_status,:operation_name, :order_id, :created, :operation_object)

                              """
            db.session.execute(text(sql_insert),
                               {'execution_status': execution_status, 'operation_name': operation_name,
                                'order_id': order_id, 'created': created, 'operation_object': operation_object})
        except Exception, e:
            current_app.logger.error(u'数据存入异常:{}'.format(e), exc_info=True)
            return e

    @classmethod
    def finished_order_log(cls, args):
        """
        wei lai 2016/12/14
        功能：创建订单日志
        """
        order_id = args['order_id']
        operation_object = args['operation_object']
        operation_name = args['operation_name']
        execution_status = args['execution_status']
        now = datetime.datetime.now()
        finished = now.strftime("%Y-%m-%d %H:%M:%S")

        sql_insert = u"""INSERT INTO dis_order_log(execution_status,`operation_name`,`order_id`,`finished`,`operation_object`)
                             VALUES (:execution_status,:operation_name, :order_id, :finished, :operation_object)
                      """
        db.session.execute(text(sql_insert),
                           {'execution_status': execution_status, 'operation_name': operation_name,
                            'order_id': order_id, 'finished': finished, 'operation_object': operation_object})

    @classmethod
    def get_order_log(cls, order_id):
        """
        wei lai 2016/12/14
        功能：根据订单ID查询订单日志（订单跟踪）
        """
        sql = u"""
                SELECT log1.id,log1.order_id,log1.operation_name,log1.operation_object,log1.created,
                 log2.execution_status, log2.finished FROM `dis_order_log` log1
                left join dis_order_log log2 on log1.order_id=log2.order_id
                AND log1.operation_name=log2.operation_name and log1.operation_object=log2.operation_object and log1.id != log2.id
                where log1.order_id = :order_id and log1.execution_status='doing'  order by log1.created  DESC,log1.id  DESC
            """
        data_list = db.session.execute(text(sql), {'order_id': order_id})
        return data_list

    @classmethod
    def update_operation_name(cls, args):
        """
        wei lai 2016/12/14
        功能：创建订单日志
        """
        order_id = args['order_id']
        operation_object = args['operation_object']
        operation_name = args['operation_name']
        execution_status = args['execution_status']
        a = chr(random.randint(97, 122))
        b = str(random.randint(10, 99))
        c = chr(random.randint(97, 122))
        operation_object_new = operation_object+u'['+u'失败'+a+b+c+u']'
        sql_insert = u"""UPDATE dis_order_log  SET operation_object =:operation_object_new WHERE order_id = :order_id and
                        operation_name = :operation_name and operation_object = :operation_object
                         """
        db.session.execute(text(sql_insert),
                           {'execution_status': execution_status, 'operation_name': operation_name,
                            'order_id': order_id, 'operation_object_new': operation_object_new,
                            'operation_object': operation_object})

    @classmethod
    def check_tenant_order(cls, tenant_name):
        """
        wei lai 2017/2/23
        功能：检查租户下是否有未完成的订单
        """
        resource_type = ResourceType.Logic_Pool.value
        status = OrderStatus.doing
        status1 = OrderStatus.failure
        tenant_names = u''.join([tenant_name, '[%'])
        sql = u"""select DISTINCT o.id,o.* from dis_order o,dis_order_log ol where o.id = ol.order_id and
              (ol.operation_object = :tenant_name or ol.operation_object like :tenant_names) and o.resource_type = :resource_type and (o.`status` = :status or
              o.`status` = :status1)
              and o.operation_type = 'tenant_resource'
                                 """
        data_list = db.session.execute(text(sql), {'tenant_name': tenant_name, 'resource_type': resource_type
                                                   , 'status': status,'status1': status1,'tenant_names':tenant_names })
        return data_list

