# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
    sxw 2016-7-5
    存储一些成员测试实例，提供给单元测试以及集成测试使用
    eg.
        云平台成员
        租户成员
"""
import datetime
import pytest

from app.user.member.models import CmdbUser


@pytest.fixture()
def user(session):
    """新建一个用户"""
    user_ = CmdbUser(id=10001, name=u"张三",
                     status=u"正常", sex=u"男",
                     email="123456@qq.com", employ_date=datetime.datetime.now().date(),
                     passwd="123456", sulogin=0, tmp_tenant=100000)
    # session.add(user_)
    # session.commit()
    user_.save()
    return user_


@pytest.fixture
def admin():
    """test admin"""
    return ""
