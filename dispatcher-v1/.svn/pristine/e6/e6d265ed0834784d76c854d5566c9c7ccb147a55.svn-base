# !/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from app.extensions import db
from app.utils.database import CRUDMixin


class PhysicalCluster(CRUDMixin):

    @classmethod
    def create_volume_group(cls, args):
        data = None
        try:
            sql = u"""
                insert into cmdb_pm_cluster(name, description, created, application_id, logicpool_id)
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
                update cmdb_pm_cluster a set a.name=:name,a.description=:description
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
                update cmdb_pm_cluster a set a.removed=:removed
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