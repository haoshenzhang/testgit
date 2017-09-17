#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    models
"""
from app.extensions import db
from app.utils.database import CRUDMixin
from sqlalchemy import text
from app.utils.format import FormatService
from app.utils.format import format_result

class AsyncTask1(db.Model, CRUDMixin):
    """
        wyj 2016-12
            调用TASK
    """
    __tablename__ = 'com_async_task'

    @staticmethod
    def update_result(id):

        sql_update = u"""
                    UPDATE com_async_task SET `status`='FINISH' and result = '{"f5_id": 35}' and code = 1
                    WHERE id=:id
                    """
        db.session.execute(text(sql_update),{'id': id})
        db.session.commit()

    @staticmethod
    def select_id(order_id):
        sql = u"""
              SELECT id FROM com_async_task
              WHERE order_id = :order_id
              """
        res = db.session.execute(text(sql), {'order_id': order_id})
        res = format_result(res)
        return res[0]