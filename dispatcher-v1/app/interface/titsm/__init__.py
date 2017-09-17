# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -03-30
"""
from flask.ext.restful import Api

from app.exceptions import errors
from app.interface import interface_app_bp
from app.interface.titsm.view import TitsmTicketApp

titsm = Api(interface_app_bp, prefix='/interface', errors=errors)
# 添加rest资源


titsm.add_resource(TitsmTicketApp, '/status')