# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    songxiaowei 2017-03-24

    自定义logger公共方法，提供需要记录日志模块调用
"""
import functools
from six.moves import http_client

import datetime
from flask import json, request

from app.configs.code import ResponseCode
from app.extensions import db
from app.utils.helpers import DBEnum


class ActionType(DBEnum):
    """
        songxiaowei 2017-03-24

        定义操作类型规范，限制必须使用规定操作类型
        调用举例:
            ActionType.create.value 创建
    """
    create = u"创建"
    update = u"修改"
    delete = u"删除"
    login = u"登录"
    logout = u"登出"
    disk_add = u"扩容"
    relevance = u"关联"
    restore = u"备份还原"
    bound = u"绑定"
    unbound = u"解绑"


class ResourceType(DBEnum):
    """
    wei lai 2016/12/14

    定义日志操作类型
    调用举例:
            ResourceType.logic_pool.value 创建
    """
    logic_pool = u"客户资源池"
    logic_server = u"逻辑服务器"
    volume = u"磁盘卷"
    ip_segment = u"内网IP段"
    ip = u"IP"
    vpc = u"VPC"
    subnet = u"子网"
    fw_policy = u"防火墙策略"
    LB_policy = u"负载均衡策略"
    backup_policy = u"备份策略"
    bigeye_policy = u"监控策略"
    vpn = u"VPN"
    vpn_policy = u"VPN策略"
    pm_cluster = u"物理集群"
    public_ip = u"公网IP"
    pm = u"物理机"
    security_service = u"安全服务项"
    vm = u"虚拟机"
    travel_cloud = u"航信云"
    recycle_policy = u"回收站策略"
    flavor = u"配置CPU&Mem"
    image = u"镜像"
    zone = u"ZONE"
    template = u"模板"
    environment = u"底层环境"
    tenant_resource = u"用户资源"


def log_decorator(action, resource, id_name=None):
    """
        songxiaowei 2017-03-24

        用户操作装饰器，在必要资源处的view method方法之上添加并且填写相关参数
        创建操作由于id是不存在的，所以无需传递
        删初、修改改操作必须传递前端传递给后端的对应资源id
        使用举例:
            class UserApi(Resource):
            \"""管理用户模块
            \"""

                @log_decorator(action=ActionType.create.value, resource=ResourceType.logic_pool.value)
                @staticmethod
                def post():
                    \"""创建操作\"""
                    pass
                @log_decorator(action=ActionType.delete.value, resource=ResourceType.logic_pool.value, id_name="id")
                @staticmethod
                def delete():
                    \"""删除操作\"""
                    pass
    """
    def log_wrapper(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # 进入方法前做一些操作
            from flask import current_app, g
            if current_app.config.get('SERVICE_LOG_ENABLED'):
                from app.log_.models import ComUserLog
                # 校验action是否符合要求
                message = ('action={action}不在ActionType枚举中，请检查再试! '.format(action=action))
                if action not in ActionType.enums:
                    raise TypeError(message)
                message = ('resource={resource}不在ResourceType枚举中，请检查再试! '.format(resource=resource))
                if resource not in ResourceType.enums:
                    raise TypeError(message)
                from app.log_.constant import RequestMethod
                message = ('请求方法为Method={method}，非法记录用户操作日志请求类型! '.format(method=request.method))
                if request.method.upper() == RequestMethod.get.value:
                    raise TypeError(message)
                log = ComUserLog(action=action, resource=resource, id_name=id_name)
            # 执行方法
            result = f(*args, **kwargs)
            # 扫尾工作
            if current_app.config.get('SERVICE_LOG_ENABLED'):
                log.update_date = datetime.datetime.now()
                from app.log_.constant import LogLevel
                if u"application/json" in result.content_type:
                    if result.status_code == http_client.OK:
                        d = json.loads(result.get_data())
                        if isinstance(d, dict) and "status" in d:
                            log.result_code = str(d["status"])
                            # 根据返回结果值置日志相应等级
                            if d["status"] == str(ResponseCode.SUCCEED):
                                log.level = LogLevel.info.value
                                serial_dict = {}
                                if "data" in d and "serial_number" in d["data"]:
                                    serial_dict = {"serial_number": d["data"]["serial_number"]}
                                elif "data" in d and "id" in d["data"]:
                                    serial_dict = {"id": d["data"]["id"]}
                                elif "data" in d and "task_id" in d["data"]:
                                    serial_dict = {"task_id": d["data"]["task_id"]}
                                log.operation.update(serial_dict)
                                if all(map(lambda x: x not in log.operation, ("id", "serial_number", "task_id"))):
                                    log.operation.update({"error": u"返回订单格式不对，请联系后台人员！"})
                            # 此处可以规范返回错误值，例如参数校验失败，返回10002，就将日志等级置为警告
                            elif d["status"] == str(ResponseCode.VALIDATE_FAIL):
                                log.level = LogLevel.warning.value
                            else:
                                log.level = LogLevel.error.value
                        if isinstance(d, dict) and "message" in d:
                            log.result_msg = d["message"]
                log.save(commit=True)
            return result
        return wrapper
    return log_wrapper
