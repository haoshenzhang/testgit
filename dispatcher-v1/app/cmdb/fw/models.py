# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    虚拟机cmdb
"""

from app.deployment.models import ComAsyncTask
from app.extensions import db
from sqlalchemy import text
from app.utils.database import CRUDMixin
from app.utils.format import FormatService
from app.utils.format import format_result
from app.catalog.volume.models import CmdbVolume
from flask import current_app
from app.order.constant import OrderStatus
import datetime
import json


class CmdbFw(db.Model, CRUDMixin):
    __tablename__ = 'net_firewall_policy_main'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    description = db.Column(db.String(100))
    status = db.Column(db.String(10), nullable=False)
    virtual_fw_policy_id = db.Column(db.Integer)
    physical_fw_policy_id = db.Column(db.Integer)
    sg_policy_id = db.Column(db.Integer)
    source_ip_addr = db.Column(db.String(40), nullable=False)
    target_ip_addr = db.Column(db.String(40), nullable=False)
    source_port_range = db.Column(db.String(255), nullable=False)
    target_port_addr = db.Column(db.String(255), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    ip_version = db.Column(db.String(10), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    removed = db.Column(db.DateTime)
    vpc_id = db.Column(db.Integer, nullable=False)



    @staticmethod
    def insert_fw_main(args,order_id):
        application_id = None
        if args.get("application_id"):
            application_id = args["application_id"]
        application_name = None
        if args.get("application_name"):
            application_name = args["application_name"]
        direction = args["direction"]
        description = args['description']
        vpc_id = args['vpc_id']
        target_port_addr = ','.join(args['port'])
        source_ip_addr = ','.join(args['src'])
        target_ip_addr = ','.join(args['dst'])
        status = OrderStatus.succeed
        now = datetime.datetime.now()
        created = now.strftime("%Y-%m-%d %H:%M:%S")
        source_port_range = 'any'
        ip_version = 'Ipv4'
        protocol = ','.join(args['protocol'])
        action = args['action']
        fw_info = CmdbFw.select_fw_info(order_id)
        sg_policy_id = 0
        virtual_fw_policy_id=0
        physical_fw_policy_id=0
        name = ''
        for f in fw_info:
            if f['node_name'] == 'security_group'and f['execute_parameter']:
                sg_policy_id = json.loads(f['execute_parameter'])['security_group_policy_id']
                name =CmdbFw.select_sg_name(sg_policy_id)
            if f['node_name'] == 'v_fw'and f['execute_parameter']:
                virtual_fw_policy_id = json.loads(f['execute_parameter'])['vfw_id']
                name =CmdbFw.select_vfw_name(virtual_fw_policy_id)
            if f['node_name'] == 'fw'and f['execute_parameter']:
                physical_fw_policy_id = json.loads(f['execute_parameter'])['fw_id']
                name =CmdbFw.select_fw_name(physical_fw_policy_id)
        sql_insert = u"""INSERT INTO net_firewall_policy_main (`name`,`description`,`status`,`source_ip_addr`,`target_ip_addr`,`source_port_range`,`target_port_addr`, `protocol`,`action`,`ip_version`,`created`,`vpc_id`,`direction`)
                      VALUES (:name,:description,:status,:source_ip_addr,:target_ip_addr,:source_port_range,:target_port_addr, :protocol,:action,:ip_version,:created,:vpc_id,:direction)
                  """
        main_id = db.session.execute(text(sql_insert), {'name': name, 'description': description,
                                                   'status': status, 'source_ip_addr': source_ip_addr,
                                                   'target_ip_addr': target_ip_addr, 'source_port_range': source_port_range, 'target_port_addr': target_port_addr,
                                                   'protocol': protocol, 'action': action, 'ip_version':ip_version,
                                                   'created': created,'vpc_id': vpc_id, 'direction':direction})
        main_id = main_id.lastrowid
        if sg_policy_id:
            sql_update = u"""
                    UPDATE net_firewall_policy_main SET `sg_policy_id`=:sg_policy_id
                    WHERE id=:id
                    """
            db.session.execute(text(sql_update),{'id': main_id, 'sg_policy_id': sg_policy_id})
        if virtual_fw_policy_id:
            sql_update = u"""
                    UPDATE net_firewall_policy_main SET `virtual_fw_policy_id`=:virtual_fw_policy_id
                    WHERE id=:id
                    """
            db.session.execute(text(sql_update),{'id': main_id, 'virtual_fw_policy_id': virtual_fw_policy_id})
        if physical_fw_policy_id:
            sql_update = u"""
                    UPDATE net_firewall_policy_main SET `physical_fw_policy_id`=:physical_fw_policy_id
                    WHERE id=:id
                    """
            db.session.execute(text(sql_update),{'id': main_id, 'physical_fw_policy_id': physical_fw_policy_id})

    @staticmethod
    def select_fw_info(order_id):
        sql = u"""
              SELECT node_name, execute_parameter FROM dis_process_task_item task
              WHERE task.order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id':order_id})
        res = format_result(res)
        return res

    @staticmethod
    def select_fw_name(id):
        sql = u"""
              SELECT name FROM net_firewall_policy fw
              WHERE fw.id = :id
              """
        res = db.session.execute(text(sql), {'id':id})
        res = format_result(res)
        return res[0]['name']

    @staticmethod
    def select_vfw_name(id):
        sql = u"""
              SELECT name FROM net_v_firewall_policy vfw
              WHERE vfw.id = :id
              """
        res = db.session.execute(text(sql), {'id':id})
        res = format_result(res)
        return res[0]['name']

    @staticmethod
    def select_sg_name(id):
        sql = u"""
              SELECT name FROM net_security_group_policy sg
              WHERE sg.id = :id
              """
        res = db.session.execute(text(sql), {'id':id})
        res = format_result(res)
        return res[0]['name']

    @staticmethod
    def update_fw_main(id):
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_update = u"""
                    UPDATE net_firewall_policy_main SET `removed`=:removed , `status`= 'succeed'
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': id, 'removed': removed})
