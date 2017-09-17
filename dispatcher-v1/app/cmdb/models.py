# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
   cmdb表
"""
from app.extensions import db
from sqlalchemy import text
import datetime

class Dis_Alloc(object):

    @staticmethod
    def delete_alloc(order_id):
        now = datetime.datetime.now()
        removed = now.strftime("%Y-%m-%d %H:%M:%S")
        sql_update = u"""
                UPDATE dis_resource_allocate SET `removed`= :removed
                WHERE order_id=:order_id
                """
        db.session.execute(text(sql_update),
                           {'order_id': order_id, 'removed': removed})
        db.session.commit()

