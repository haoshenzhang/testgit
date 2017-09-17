# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    yg -03-30
"""
from flask import request
from flask.ext.restful import Resource

from app.deployment.models import ComAsyncTask

# TITSM回调接口
class TitsmTicketApp(Resource):

    @staticmethod
    def post():
        args = request.json
        com_async_task_id = args['TaskID']
        ComAsyncTask.update_async_task(com_async_task_id, 'FINISH', 1, str(args))
