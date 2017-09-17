# -*- coding: utf-8 -*-
"""
    sxw 2016-7-7

    返回关键字和返回代码
"""


class ResponseKey(object):
    """返回关键字."""
    STATUS = "code"
    MESSAGE = "msg"
    LEVEL = "level"


class ResponseCode(object):
    """返回代码"""
    # 数据库异常错误代码
    FLASK_SQLALCHEMY_EXCEPT = 3306

    # 异常请求错误代码
    URL_NOT_FOUND = 404             # 该请求不存在
    BAD_REQUEST = 400               # 错误的请求，请求格式不规范，不符合API要求
    METHOD_NOT_ALLOWED = 405        # 请求的方式错误
    CSRF_TOKEN_MISSING = 40000      # CSRF token missing or incorrect

    # 全局错误代码块
    SUCCEED = 10000                 # 成功
    ERROR = 10001                   # 失败
    VALIDATE_FAIL = 10002           # 数据校验失败
    GET_BY_PARAM_ERROR = 10003      # 根据参数获取结果失败，数据不存在
    SYSTEM_ERROR = 500

    # 认证模块代码块
    NO_AUTHENTICATED = 20001        # 未认证

    # user/department 部门管理 jiangxp 2016.7.20
    CAN_NOT_DELETE_DEPARTMENT = 10004  # 不能删除该部门，因为有子部门存在
    CAN_NOT_ADD_DEPARTMENT = 10005  # 部门名称已经存在，不能添加
    CAN_NOT_ADD_OPENSTAK = 10006  # OPENSATCK名称已经存在，不能添加

    # 资源池 jiangxp 2016.7.22
    TYPE_CAN_NOT_BE_NULL = 10006    # 资源池类型不能为空
    RESOURCE_POOL_TYPE_NOT_EXIST = 10007  # 资源池类型不存在
    RESOURCE_POOL_NAME_EXIST = 10008  # 资源池名称已经存在
    RESOURCE_POOL_NAME_CAN_NOT_BE_NULL = 10009  # 资源池名称已经存在

    # 权限 JIANGXP 2016.8.10
    NO_PER = 100010

    TOKEN_CREDENTIALS_EXCEPT = 40001  # access token凭据异常


class ResponseLevel(object):
    """
    sxw 2016-7-7

    定义错误等级
    """
    INFO = "info"
    DANGER = "danger"
