# !/usr/bin/python
# -*- coding: utf-8 -*-

"""
预处理数据
"""
from app.utils import format
from app.extensions import db
from sqlalchemy import text
from app.process.models import ProcessMappingTaskItem

class VM_Inf_Item_List(ProcessMappingTaskItem):
    pass