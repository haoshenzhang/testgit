#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    models
"""
from app.extensions import db
from app.utils.database import CRUDMixin
from sqlalchemy import text
from app.utils.format import FormatService

class AsyncTask(db.Model, CRUDMixin):
    __tablename__ = 'com_async_task'


    @staticmethod
    def get_async_task_status(task_id):
        sql = u"""
            Select * From com_async_task WHERE id = :id
        """
        res = db.session.execute(text(sql), {'id': task_id})
        result = FormatService.format_result(res)
        return result
