# !/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from app.extensions import db
from app.utils.database import CRUDMixin
from app.utils.format import format_result


class VolumeGroup(CRUDMixin):

    @classmethod
    def create_vpn(cls, args):
        data = None
        try:
            sql = u"""
                insert into cmdb_volumegroup(name, description, created, application_id, logicpool_id)
                values(:name, :description, :created, :application_id, :logicpool_id)
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
    def update_volume_group(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_volumegroup a set a.name=:name,a.description=:description
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
    def delete_volume_group(cls, args):
        data = None
        try:
            sql = u"""
                update cmdb_volumegroup a set a.removed=:removed
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
                select * from cmdb_volumegroup a
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
    def create_volume_server_ref(cls, args):
        data = None
        try:
            sql = u"""
                insert into cmdb_volumegroup_logicserver_ref(volumegroup_id, logicserver_id)
                values(:volumegroup_id, :logicserver_id)
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            print data
        except Exception, e:
            print e

        return data

    @classmethod
    def delete_volume_server_ref(cls, args):
        data = None
        try:
            sql = u"""
                delete from cmdb_volumegroup_logicserver_ref a where a.volumegroup_id=:volumegroup_id
                """
            # sql = cls.query.filter(MTest.id == args["id"]).all()
            # print args['sex']
            data = db.session.execute(text(sql), args)
            print data
        except Exception, e:
            print e

        return data


class NetVpnUser(CRUDMixin):
    """net_vpn_user与数据库操作"""
    @classmethod
    def list(cls, args):
        """根据租户id获取vpn列表以及高级检索"""
        sql = u""" SELECT nvu.*, nv.vpn_policy, nv.status FROM `net_vpn_user` nvu INNER JOIN net_vpn nv on nvu.vpn_id = nv.id
                  WHERE nv.tenant_id = :tenant_id AND nv.removed is NULL AND nv.`status` is NULL AND nvu.removed is NULL """
        if args['vpn_policy'] is not None:
            sql = u''.join([sql, u""" and nv.vpn_policy = :vpn_policy"""])
        if args['company_name'] is not None:
            sql = u''.join([sql, u""" and nvu.company_name = :company_name"""])
        if args['phone_number'] is not None:
            sql = u''.join([sql, u""" and nvu.phone_number = :phone_number"""])
        if args['status'] is not None:
            sql = u''.join([sql, u""" and nv.status = :status"""])
        if args['user_name'] is not None:
            args['user_name'] = u''.join(['%', args['user_name'], '%'])
            sql = u''.join([sql, u""" and nvu.user_name like :user_name"""])
        if args['description'] is not None:
            args['description'] = u''.join(['%', args['description'], '%'])
            sql = u''.join([sql, u""" and nvu.description like :description"""])
        if args['period'] is not None:
            sql = u''.join([sql, u""" and nvu.period = :period"""])
        if args['starttime'] is not None and args['endtime'] is not None:
            sql = u''.join([sql, u""" and nvu.created between :starttime and :endtime"""])
        sql = u''.join([sql, u""" ORDER BY nvu.id limit :start, :per_page"""])
        result = db.session.execute(sql, args)
        result = format_result(result)
        return result

    @classmethod
    def list_count(cls, args):
        """根据租户id或者条件查询个数"""
        sql = u""" SELECT count(nvu.id) as te FROM `net_vpn_user` nvu INNER JOIN net_vpn nv on nvu.vpn_id = nv.id
                  WHERE nv.tenant_id = :tenant_id AND nv.removed is NULL AND nv.`status` is NULL AND nvu.removed is NULL """
        if args['vpn_policy'] is not None:
            sql = u''.join([sql, u""" and nv.vpn_policy = :vpn_policy"""])
        if args['company_name'] is not None:
            sql = u''.join([sql, u""" and nvu.company_name = :company_name"""])
        if args['phone_number'] is not None:
            sql = u''.join([sql, u""" and nvu.phone_number = :phone_number"""])
        if args['status'] is not None:
            sql = u''.join([sql, u""" and nv.status = :status"""])
        if args['user_name'] is not None:
            args['user_name'] = u''.join(['%', args['user_name'], '%'])
            sql = u''.join([sql, u""" and nvu.user_name like :user_name"""])
        if args['description'] is not None:
            args['description'] = u''.join(['%', args['description'], '%'])
            sql = u''.join([sql, u""" and nvu.description like :description"""])
        if args['period'] is not None:
            sql = u''.join([sql, u""" and nvu.period = :period"""])
        if args['starttime'] is not None and args['endtime'] is not None:
            sql = u''.join([sql, u""" and nvu.created between :starttime and :endtime"""])
        total_count = db.session.execute(sql, args)
        for i in total_count:
            itc = i.te
            return itc
