# -*- coding: utf-8 -*-
from flask import current_app
from sqlalchemy import text
from app.configs.default import DefaultConfig
from app.extensions import db
from app.utils.database import CRUDMixin
from app.process.constant import IfProcess, NodeType
from app.utils import format
from app.utils.format import format_result
import json


class DisNode(db.Model, CRUDMixin):
    """
    节点定义表
    """
    __tablename__ = "dis_node"
    # 节点id
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # 类型
    node_type = db.Column(db.Enum(*NodeType.enums), nullable=False)
    operation = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # 节点名称
    node_name = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    # 超时时间,单位分钟
    timeout = db.Column(db.Integer, nullable=False, server_default=text("'0'"))

    @staticmethod
    def get_node(node_name):
        """
        获取节点细节
        :param node_name: 节点name
        :return:
        """
        sql = u"""
              SELECT n.* FROM dis_node n
              WHERE operation = 'execute' AND node_name= :node_name
              """
        res = db.session.execute(text(sql), {'node_name': node_name}).fetchone()
        if res:
            return res[0]
        else:
            return {}
    
    
class ProcessMappingNode(db.Model, CRUDMixin):
    """
    jinxin 2016-11-1
    流程定义表
    """
    __tablename__ = "dis_process_mapping_node"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    # 流程ID
    process_id = db.Column(db.Integer, nullable=False)
    # 节点ID
    node_id = db.Column(db.Integer, nullable=False)
    # 上一个节点ID，0表示没有
    last_node_id = db.Column(db.Integer, nullable=False, server_default=text("'0'"))
    # 是否是流程，默认是节点
    if_process = db.Column(db.Enum(*IfProcess.enums), nullable=False, server_default=text("'0'"))

    @staticmethod
    def get_node_detail(process_id, node_id):
        """
        获取节点细节
        :param process_id: 流程id
        :param node_id: 节点id
        :return:
        """
        sql = u"""
              SELECT p.*, n.node_type, n.operation, n.node_name, n.timeout FROM dis_process_mapping_node p
              JOIN dis_node n ON n.id=p.node_id
              WHERE process_id = :process_id AND node_id= :node_id
              """
        res = db.session.execute(text(sql), {'process_id': process_id, 'node_id': node_id}).fetchone()
        if res:
            return res[0]
        else:
            return {}

    @staticmethod
    def get_node_list( process_id):
        """
        获取流程下的节点列表
        :param process_id:
        :return:
        """
        sql = u"""
              SELECT p.*, n.node_type, n.operation, n.node_name, n.timeout FROM dis_process_mapping_node p
              LEFT JOIN dis_node n ON n.id=p.node_id
              WHERE p.process_id = :process_id
              """
        res = db.session.execute(text(sql), {'process_id': process_id})
        res = format.FormatService.format_result(res)
        if not res:
            current_app.logger.info(u"未找到流程")
        return res
        
        
class ProcessMappingTask(db.Model, CRUDMixin):
    """
    每个订单的task表
    """
    __tablename__ = "dis_process_task"
    
    order_id = db.Column(db.Integer, nullable=False, primary_key=True)
    service = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    status = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    parameters = db.Column(db.TEXT(), nullable=False)

    @staticmethod
    def insert(order_id, service, status, parameters):
        sql_insert = u"""
                    INSERT INTO dis_process_task(order_id, `service`, `status`, `parameters`)
                    VALUES (:order_id, :service, :status, :parameters)
                    """
        db.session.execute(text(sql_insert),
                                   {'order_id': order_id, 'status': status, 'service': service, 'parameters': parameters})
        db.session.commit()

    @staticmethod
    def update_status(status, order_id, old_status):
        """
        更新订单状态
        :param status:
        :param order_id:
        :param old_status:
        :return:
        """
        sql_update = u"""
                    UPDATE dis_process_task SET `status`=:status
                    WHERE order_id=:order_id AND status in (:old_status)
                    """
        db.session.execute(text(sql_update),
                                   {'order_id': order_id, 'status': status, 'old_status': old_status})
        db.session.commit()

    @staticmethod
    def update_parameters(order_id, parameters):
        """
        根据订单更新任务 parameters 字段
        :param order_id:
        :param parameters:
        :return:
        """
        sql_update = u"""
                    UPDATE dis_process_task SET `parameters`=:parameters
                    WHERE order_id=:order_id
                    """
        db.session.execute(text(sql_update),
                                   {'order_id': order_id, 'parameters': parameters})
        db.session.commit()

    @staticmethod
    def update_execute_parameters(order_id, parameters):
        """
        根据订单更新任务 parameters 字段
        :param order_id:
        :param parameters:
        :return:
        """
        sql_update = u"""
                    UPDATE dis_process_task SET `execute_parameters`=:execute_parameters
                    WHERE order_id=:order_id
                            """
        db.session.execute(text(sql_update),
                           {'order_id': order_id, 'parameters': parameters})
        db.session.commit()

    @staticmethod
    def get_task_status(order_id):
        """
        根据订单获取任务状态
        :param order_id:
        :return:
        """
        sql = u"""
              SELECT status FROM dis_process_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format.FormatService.format_result(res)
        if res:
            return res[0]
        else:
            return None
    
    @staticmethod
    def get_task_data(order_id):
        """
        根据订单获取task表中 parameters字段
        :param order_id:
        :return:
        """
        sql = u"""
              SELECT parameters FROM dis_process_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id}).fetchone()
        if res:
            return res[0]
        else:
            return {}

    @staticmethod
    def get_task_execute_data(order_id):
        """
        根据订单获取task表中 execute_parameters
        :param order_id:
        :return:
        """
        sql = u"""
              SELECT execute_parameters FROM dis_process_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id}).fetchone()
        if res:
            return res[0]
        else:
            return {}

    @staticmethod
    def get_task_info(order_id):
        """
        根据订单获取 parameters
        :param order_id:
        :return:
        """
        sql = u"""
              SELECT parameters FROM dis_process_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format.FormatService.format_result(res)
        params = json.loads(res[0]['parameters'])
        return params


class ProcessMappingTaskItem(db.Model, CRUDMixin):
    """
    jinxin 2016-11-1
    每个订单的task表
    """
    __tablename__ = "dis_process_task_item"
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    order_id = db.Column(db.Integer, nullable=False)
    process_id = db.Column(db.Integer, nullable=False)
    node_id = db.Column(db.Integer, nullable=False)
    last_node_id = db.Column(db.Integer, nullable=False)
    key = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    node_name = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    status = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    @staticmethod
    def insert( order_id, process_id, node_id, node_name, status, key, last_node_id, timeout):
        """
        插入新数据
        :param order_id:
        :param process_id:
        :param node_id:
        :param node_name:
        :param status:
        :param key:
        :param last_node_id:
        :param timeout:
        :return:
        """
        key = u'todo '
        sql_insert = u"""
                    INSERT INTO dis_process_task_item(order_id, process_id, node_id, `node_name`, `status`,
                         `key`, last_node_id, timeout)
                    VALUES (:order_id, :process_id, :node_id, :node_name, :status, :key, :last_node_id, :timeout)
                    """
        db.session.execute(text(sql_insert), {'order_id': order_id, 'process_id': process_id,\
                                              'node_id': node_id, 'node_name': node_name, \
                                              'status': status, 'key': key, 'last_node_id': last_node_id,\
                                              'timeout': timeout})
        db.session.commit()

    @staticmethod
    def get_task_node(order_id, node_id):
        """
        根据订单以及节点获取item表中的数据
        :param order_id:
        :param node_id:
        :return:
        """
        sql = u"""
              SELECT * FROM dis_process_task_item
              WHERE order_id = :order_id AND node_id= :node_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id, 'node_id': node_id})
        res = format.FormatService.format_result(res)
        return res

    @staticmethod
    def get_task_node2(order_id, last_node_id):
        """
        根据订单和上一个节点获取item表中数据
        :param order_id:
        :param last_node_id:
        :return:
        """
        sql = u"""
              SELECT i.*,n.timeout FROM dis_process_task_item i LEFT JOIN dis_node n ON n.id = i.node_id
              WHERE order_id = :order_id AND last_node_id= :last_node_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id, 'last_node_id': last_node_id})
        res = format.FormatService.format_result(res)
        return res

    @staticmethod
    def get_task_item_list(order_id):
        """
        根据订单获取item表中的所有数据
        :param order_id:
        :return:
        """
        sql = u"""
              SELECT * FROM dis_process_task_item
              WHERE order_id = :order_id
              ORDER BY id ASC
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        return res

    @staticmethod
    def get_task_item_list_by_node_name(order_id,node_name):
        """
        根据订单以及节点获取item中execute_parameter字段
        :param order_id:
        :param node_name:
        :return:
        """
        sql = u"""
              SELECT execute_parameter FROM dis_process_task_item
              WHERE order_id = :order_id AND node_name = :node_name
              ORDER BY id ASC
              """
        res = db.session.execute(text(sql),{'order_id':order_id,'node_name':node_name})
        res = format_result(res)
        return res

    @staticmethod
    def get_task_list(order_id):
        sql = u"""
              SELECT * FROM dis_process_task_item
              WHERE order_id = :order_id
              ORDER BY id ASC
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format.FormatService.format_result(res)
        return res


    @staticmethod
    def get_status(order_id, process_id, node_id, key):
        sql = u"""
              SELECT status FROM dis_process_task_item
              WHERE order_id = :order_id AND process_id=: process_id AND node_id=:node_id AND key=:key
              """
        res = db.session.execute(text(sql), {'order_id': order_id, 'process_id': process_id, 'node_id': node_id, 'key': key})
        res = format.FormatService.format_result(res)
        if res:
            return res[0]
        else:
            return None

    @staticmethod
    def delete(order_id):
        """
        根据订单删除所有item
        :param order_id:
        :return:
        """
        sql_delete = u"""
                    DELETE dis_process_task_item
                    WHERE order_id=:order_id
                    """
        db.session.execute(text(sql_delete),
                                   {'order_id': order_id})
        db.session.commit()

    @staticmethod
    def update_status(status, order_id, task_item_id, old_status):
        """
        更新item状态
        :param status:
        :param order_id:
        :param task_item_id:
        :param old_status:
        :return:
        """
        sql_update = u"""
                    UPDATE dis_process_task_item SET `status`=:status
                    WHERE `order_id` = :order_id AND `id`= :id AND `status`= :old_status
                    """
        db.session.execute(text(sql_update),
                                   {'status':status ,'order_id': order_id, 'id': task_item_id, 'old_status': old_status})
        db.session.commit()

    @staticmethod
    def update_error_status(order_id):
        sql_update = u"""
                    UPDATE dis_process_task_item SET `status`=:status
                    WHERE `order_id` = :order_id AND `status` in ('failed','timeout')
                    """
        db.session.execute(text(sql_update),
                           {'status': 'waiting', 'order_id': order_id})
        db.session.commit()

    @staticmethod
    def update_execute_parameter(order_id,task_item_id,para):
        sql_update = u"""
                    UPDATE dis_process_task_item SET `execute_parameter`= :execute_parameter
                    WHERE `order_id` = :order_id AND `id`= :id
                    """
        db.session.execute(text(sql_update),
                           {'execute_parameter':para, 'order_id': order_id, 'id': task_item_id})
        db.session.commit()

    @staticmethod
    def query_all_execute_parameter(order_id):
        sql = u"""

        """
        

class ProcessMappingTenant(db.Model, CRUDMixin):
    """
    jinxin 2016-11-1
    每个租户自定义每种资源的流程配置表
    """
    __tablename__ = "dis_process_tenant"
    
    tenant_id = db.Column(db.Integer, nullable=False)
    process_id = db.Column(db.Integer, nullable=False, primary_key=True)
    type = db.Column(db.String(30, DefaultConfig.SQLALCHEMY_DATABASE_CHAR_CODE), nullable=False)

    @staticmethod
    def get_process_id(tenant_id, server_name):
        """
        根据租户以及服务名称获取流程id
        :param tenant_id:
        :param server_name:
        :return:
        """
        sql = u"""
              SELECT process_id FROM dis_process_tenant
              WHERE tenant_id = :tenant_id AND type = :server_name
              """
        res = db.session.execute(text(sql), {'tenant_id': tenant_id, 'server_name': server_name}).first()
        if not res:
            sql = u"""
              SELECT process_id FROM dis_process_tenant
              WHERE tenant_id = -1 AND type = :server_name
              """
            res = db.session.execute(text(sql), {'server_name': server_name}).first()
        return res[0]
