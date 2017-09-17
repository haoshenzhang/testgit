# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
zone模型层
"""
import datetime

from sqlalchemy import text

from app.extensions import db
from app.management.logicpool.constant import PoolProperty
from app.utils.database import CRUDMixin


class InfZone(db.Model, CRUDMixin):
    """
    zone信息列表
    """
    __tablename__ = 'inf_zone'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    status = db.Column(db.Enum(u'enable', u'disable'), nullable=False, server_default=text("'enable'"))
    desc = db.Column(db.String(50))

    @classmethod
    def created_zone(cls, name_, location, status, desc_):
        """
        weilai
        :param name_: 名称
        :param location: 地点
        :param status: zone状态（enable，disable）
        :param desc_: zone描述
        :return:
        """
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_insert = u"""insert into inf_zone(`name`, `location`, `created`, `status`, `desc`) VALUES(:name_, :location,
                        :created, :status, :desc_)
                    """
        result = db.session.execute(text(sql_insert), {'name_': name_, 'location': location,
                                              'created': created, 'status': status, 'desc_': desc_})
        zone_id = result.lastrowid
        return zone_id

    @classmethod
    def get_zone_list(cls):
        """
        weilai
        查询zone列表
        :return: zone列表
        """
        sql = u"""
            select * from inf_zone z WHERE z.removed is null order by z.created DESC
            """
        data = db.session.execute(text(sql))
        return data

    @classmethod
    def get_zone_by_id(cls, id_):
        """
        weilai
        查询zone根据zone——id
        :return: zone列表
        """
        sql = u"""
                select * from inf_zone z WHERE z.removed is null and z.id = :id_
                """
        data = db.session.execute(text(sql), {'id_': id_})
        return data

    @classmethod
    def get_enable_zone_list(cls):
        """
        weilai
        查询可用zone列表
        :return: zone列表
        """
        status = PoolProperty.enable
        sql = u"""
                select * from inf_zone z WHERE z.status = :status and z.removed is null
                """
        data = db.session.execute(text(sql), {'status': status})
        return data

    @classmethod
    def get_zone_by_name(cls, name, zone_id):
        """
        weilai
        查询zone 通过名字
        :return: zone列表
        """
        sql = u"""
               select * from inf_zone z WHERE z.name = :name and z.removed is null and z.id != :zone_id
               """
        data = db.session.execute(text(sql), {'name': name, 'zone_id': zone_id})
        return data

    @classmethod
    def get_zone_by_names(cls, name):
        """
        weilai
        查询zone 通过名字
        :return: zone列表
        """
        sql = u"""
                  select * from inf_zone z WHERE z.name = :name and z.removed is null
                  """
        data = db.session.execute(text(sql), {'name': name})
        return data

    @classmethod
    def get_zone_by_location(cls, location):
        """
        weilai
        查询zone 通过location
        :return: zone列表
        """
        sql = u"""
                   select * from inf_zone z WHERE z.location = :location and z.removed is null
                   """
        data = db.session.execute(text(sql), {'location': location})
        return data

    @classmethod
    def update_zone(cls, name_, id_):
        """
        修改zone名称及地点
        :param name_: zone名称
        :param id_: zone id
        :return:
        """
        sql = u"""update inf_zone set `name` = :name_  where id = :id_
            """
        db.session.execute(text(sql), {'name_': name_, 'id_': id_})

    @classmethod
    def update_zone_status(cls, status, id_):
        """
        修改zone状态
        :param status
        :param id_
        :return:
        """
        sql = u"""update inf_zone set status = :status where id = :id_
               """
        db.session.execute(text(sql), {'status': status, 'id_': id_})
        db.session.commit()

    @classmethod
    def update_pool_status(cls, status, id_):
        """
        修改zone下的资源池状态
        :param status
        :param id_
        :return:
        """
        sql = u"""update inf_logic_pool set status = :status where zone_id = :id_ and removed is  NULL
                  """
        db.session.execute(text(sql), {'status': status, 'id_': id_})

    @classmethod
    def delete_zone(cls, id_):
        """
        weilai
        删除zone
        :param id_: zone的ID
        :return:
        """
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        status = PoolProperty.disable
        sql = u"""update inf_zone set removed = :removed , status = :status where id = :id_
                       """
        db.session.execute(text(sql), {'removed': removed, 'id_': id_, 'status': status})

    @classmethod
    def get_zone_pool_ref(cls, id_):
        """
        weilai
        删除时判断zone下是否有关联的资源池
        :param id_: zone ID
        :return: zone关联的资源池列表
        """
        sql = u"""
                    select * from inf_logic_pool  WHERE zone_id = :id_ and removed is  NULL
                    """
        data = db.session.execute(text(sql), {'id_': id_})
        return data

    @classmethod
    def get_zone_vc_ref(cls, id_):
        """
        weilai
        删除时判断zone下是否有关联的vc
        :param id_: zone ID
        :return: zone关联的资源池列表
        """
        sql = u"""
                        select * from inf_vmware_vc  WHERE zone_id = :id_ and removed is  NULL
                        """
        data = db.session.execute(text(sql), {'id_': id_})
        return data

    @classmethod
    def get_zone_env_ref(cls, id_):
        """
        weilai
        删除时判断zone下是否有关联的env
        :param id_: zone ID
        :return: zone关联的资源池列表
        """
        sql = u"""
                           select * from inf_openstack_env  WHERE zone_id = :id_ and removed is  NULL
                           """
        data = db.session.execute(text(sql), {'id_': id_})
        return data
