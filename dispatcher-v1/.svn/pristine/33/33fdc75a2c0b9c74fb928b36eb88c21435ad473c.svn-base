#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.exceptions

    sxw 2016-7-7

    定义异常类，所有的定义异常，请继承AppError.
"""
from werkzeug.exceptions import HTTPException, Forbidden


class AppError(HTTPException):
    """Root exception for App"""
    description = "An internal error has occured"


class AuthorizationRequired(AppError, Forbidden):
    description = "Authorization is required to access this area."


class AuthenticationError(AppError):
    description = "Invalid username and passwd combination."


"""
    sxw 2016-7-7

    绑定蓝图资源，全局捕获flask-restful中的异常并处理
"""
errors = {
    'ValueError': {
        'message': u"校验参数失败，请重试!",
        'status': 200
    },
    'AssertionError': {
        'message': u"参数格式不符合要求，请重试!",
        'status': 200
    },
    'UserAlreadyExistsError': {
        'message': "A user with that username already exists.",
        'status': 409,
    },
    'ResourceDoesNotExist': {
        'message': "A resource with that ID no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    },
}


