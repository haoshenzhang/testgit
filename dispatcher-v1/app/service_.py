#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-09-22
    公共服务层，封装公共功能
"""
from flask import current_app
from flask import g
from flask import json


class CommonService(object):
    """"
    sxw 2016-09-22

    通用服务类
    """

    @classmethod
    def _log(cls, level=u"", operation=u"", remark=u""):
        """
        sxw 2016-9-23

        用户操作日志方法

        :param level: 记录等级
        :param operation: 操作结果
        :param remark: 操作备注
        """
        if current_app.config["SERVICE_LOG_ENABLED"]:
            from app.log_.constant import LogLevel
            if level and level in LogLevel.enums:
                g.log.level = level

            if operation and isinstance(operation, dict):
                g.log.operation = json.dumps({k: v for k, v in operation.iteritems() if v})

            if remark:
                g.log.remark = remark

    @classmethod
    def log_info(cls, operation=u"", remark=u""):
        """
        sxw 2016-9-23

        用户操作记录信息日志方法

        :param operation: 操作结果
        :param remark: 操作备注
        """
        from app.log_.constant import LogLevel
        CommonService._log(LogLevel.info.value, operation, remark)

    @classmethod
    def log_error(cls, operation=u"", remark=u""):
        """
        sxw 2016-9-23

        用户操作记录错误日志方法

        :param operation: 操作结果
        :param remark: 操作备注
        """
        from app.log_.constant import LogLevel
        CommonService._log(LogLevel.error.value, operation, remark)

    @classmethod
    def log_warning(cls, operation=u"", remark=u""):
        """
        sxw 2016-9-23

        用户操作记录警告日志方法

        :param operation: 操作结果
        :param remark: 操作备注
        """
        from app.log_.constant import LogLevel
        CommonService._log(LogLevel.warning.value, operation, remark)
