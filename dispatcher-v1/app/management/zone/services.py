# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
wei lai
zone服务层
"""
from flask import current_app
from app.extensions import db
from app.management.logicpool.models import InfLogicPool
from app.management.zone.models import InfZone
from app.utils.format import format_result


class InfZoneService(object):
    """
           weilai
           InfZoneService(zone service)
       """

    @staticmethod
    def create_zone(name_, location, status, desc_):
        """
        weilai
        新建zone
        :param name_: zone名称
        :param location: zone地点
        :param status: zone状态（enable，disable）
        :param desc_: zone描述
        :return:
        """
        current_app.logger.info(u"创建zone，参数，name:{},location:{}".format(name_, location))
        current_app.logger.info(u"创建zone，参数，status:{},desc_:{}".format(status, desc_))
        zone1 = InfZone.get_zone_by_names(name_)
        zone1 = format_result(zone1)
        zone2 = InfZone.get_zone_by_location(location)
        zone2 = format_result(zone2)
        if zone1:
            current_app.logger.info(u"zone重名")
            return False, None
        if zone2:
            current_app.logger.info(u"zone地点重复")
            return False, None
        else:
            zone_id = InfZone.created_zone(name_, location, status, desc_)
            db.session.commit()
            current_app.logger.info(u"创建zone成功")
            return True, zone_id

    @staticmethod
    def get_zone_list():
        """
        weilai
        查询zone列表
        :return: zone列表
        """
        a = []
        data = InfZone.get_zone_list()
        list_ = format_result(data)
        if list_:
            for i in list_:
                d = dict()
                zone_id = i['id']
                pool_list = InfLogicPool.get_pool_by_zone(zone_id)
                pool_list = format_result(pool_list)
                d['pool_list'] = pool_list
                d['id'] = zone_id
                d['name'] = i['name']
                d['status'] = i['status']
                d['location'] = i['location']
                d['created'] = i['created']
                d['desc'] = i['desc']
                a.append(d)
        else:
            a = []
        current_app.logger.info(u"查询zone列表成功")
        return a

    @staticmethod
    def get_enable_zone_list():
        """
        weilai
        查询可用zone列表
        :return: zone列表
        """
        data = InfZone.get_enable_zone_list()
        list_ = format_result(data)
        current_app.logger.info(u"查询可用zone列表成功")
        return list_

    @staticmethod
    def update_zone(name_, id_):
        """
        修改zone名称及地点
        :param name_: zone名称
        :param location: zone地点
        :param id_: zone id
        :param desc_: zone描述
        :return:
        """
        # 重名检查
        current_app.logger.info(u"修改zone，参数，name:{}".format(name_))
        current_app.logger.info(u"修改zone，参数，id_:{}".format(id_))
        zone1 = InfZone.get_zone_by_name(name_, id_)
        zone1 = format_result(zone1)
        if zone1:
            if len(zone1) > 1:
                ss = u"zone名字已存在，请检查"
                current_app.logger.info(u"zone重名")
                return False
            if len(zone1) == 1 and str(zone1[0]['id']) != id_:
                ss = u"zone名字已存在，请检查"
                current_app.logger.info(u"zone重名")
                return False
        InfZone.update_zone(name_, id_)
        db.session.commit()
        current_app.logger.info(u"修改zone成功")
        return True

    @staticmethod
    def delete_zone(id_):
        """
        wei lai
        删除zone
        :param id_: zone ID
        :return:0：未删除zone，有关联的资源池；1：已删除
        """
        current_app.logger.info(u"删除zone，id:{}".format(id_))
        if id_:
            ids = id_.split(',')
            for zone_id in ids:
                # 资源池关联
                data = InfZone.get_zone_pool_ref(zone_id)
                list_ = format_result(data)
                # VC关联
                data1 = InfZone.get_zone_vc_ref(zone_id)
                list_1 = format_result(data1)
                # env 关联
                data2 = InfZone.get_zone_env_ref(zone_id)
                list_2 = format_result(data2)
                if list_ or list_1 or list_2:
                    current_app.logger.info(u"删除失败，该zone下有关联的资源")
                    zone = InfZone.get_zone_by_id(zone_id)
                    zone = format_result(zone)
                    zone_name = zone[0]['name']
                    return False, zone_name
            for zone_id in ids:
                InfZone.delete_zone(zone_id)
                db.session.commit()
                current_app.logger.info(u"删除成功")
            return True, u"删除成功"
        else:
            return False, u"无效id"

    @staticmethod
    def update_zone_status(status, id_):
        """
        修改zone的状态
        :param status
        :param id_
        :return:
        """
        # 查询是否有zone下关联的资源池，同时修改资源池及zone的状态
        current_app.logger.info(u"修改zone的状态参数，status:{},id_:{} ".format(status, id_))
        from app.management.logicpool.constant import PoolProperty
        if status == PoolProperty.disable:
            return False
        else:
            InfZone.update_zone_status(status, id_)
            current_app.logger.info(u"修改zone的状态参数，status:{},id_:{} ".format(status, id_))
            db.session.commit()
            return True
