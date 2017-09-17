# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    songxiaowei 2017-01-16

   子网模块之模型
"""
from app.cmdb.constant import IPStatus, IPUsage, IPNetWork, IPAppNet, IPAppLevel, IPAppCategory, IPType, IPLocation, \
    IPClass
from app.configs.default import DefaultConfig
from app.extensions import db
from app.utils.database import CRUDMixin


class CmdbIp(db.Model, CRUDMixin):
    __tablename__ = 'cmdb_ip'

    # id
    id = db.Column(db.Integer, primary_key=True)
    # ip地址
    addr = db.Column(db.String(15, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False, unique=True)
    # IP段id,对应cmdb_ip_segment表id
    segment_id = db.Column(db.Integer, nullable=False, index=True)
    # IP状态: 使用中,预分配,注销,空闲,删除,预留
    status = db.Column(db.Enum(*IPStatus.enums), nullable=False)
    # 使用: 生产,预投产,测试,UAT,办公
    usage = db.Column(db.Enum(*IPUsage.enums))
    # 网络网段: 内网,内网DMZ,InternetDMZ,企业互联DMZ,测试,大数据,管理,其他,办公网段
    network = db.Column(db.Enum(*IPNetWork.enums))
    # 网络业务系统类型: 传统业务系统,新一代共享系统,新一代CA专属系统,新一代MU专属系统,新一代CZ专属系统,新一代其它专属系统,无限制
    app_net = db.Column(db.Enum(*IPAppNet.enums))
    # 业务等级: 高等级,差异化,无限制
    app_level = db.Column(db.Enum(*IPAppLevel.enums))
    # 业务分类: WEB,APP,DB,无限制,APP_DB,LB
    app_category = db.Column(db.Enum(*IPAppCategory.enums))
    # IP类型: 物理机IP,虚拟机IP,服务IP,NASIP,设备管理IP,监控管理IP,负载均衡,SCAN IP,应用IP
    type = db.Column(db.Enum(*IPType.enums))
    # 位置: 东四,三里屯,国富瑞
    location = db.Column(db.Enum(*IPLocation.enums))
    # ip使用类型: HOSTIP,NASIP,负载均衡IP
    _class = db.Column('class', db.Enum(*IPClass.enums))
    # 对应TITSM的ID
    coss_id = db.Column(db.String(40))
    # 对应TITSM的关联策略ID
    relationship_id = db.Column(db.String(40))