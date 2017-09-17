# !/usr/bin/python
# -*- coding: utf-8 -*-
from app.extensions import db
from sqlalchemy import text

class Bigeye(object):

    @staticmethod
    def get_os_type(args):
        sql_select = u"""select ot.os_type from dis_os_template ot where ot.id = :id
                            """
        template = db.session.execute(text(sql_select), args)

        return template