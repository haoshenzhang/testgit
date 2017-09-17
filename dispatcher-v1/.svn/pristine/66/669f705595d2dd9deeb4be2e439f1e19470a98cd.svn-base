# !/usr/bin/python
# -*- coding: utf-8 -*-
import pytest
import sys
from flask_migrate import upgrade

from app.configs.testing import TestingConfig as Config

from app.application import create_app
from app.extensions import db

reload(sys)
sys.setdefaultencoding('utf8')

# ALEMBIC_CONFIG = '/migrations/alembic.ini'
ALEMBIC_CONFIG = 'alembic.ini'


# @pytest.yield_fixture(scope="function", params=None, autouse=True)
@pytest.yield_fixture(scope="session", autouse=True)
def application():
    """配置应用容器上下文"""
    app = create_app(Config)

    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()


# def apply_migrations():
#     """Applies all alembic migrations."""
#     config = Config(ALEMBIC_CONFIG)
#     upgrade(config, 'head')


@pytest.yield_fixture(scope="session")
def database(application):
    """数据库设置"""
    db.app = application

    db.create_all()  # 或许应当使用migration

    # 使用migration进行数据库ddl更改，暂时不使用
    # apply_migrations()

    # 清空各表数据，避免因为存在数据而导致测试报错

    yield db

    db.drop_all()


@pytest.yield_fixture(scope="function")
def session(database):
    connection = database.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = database.create_scoped_session(options=options)

    database.session = session

    # 事物开启自savepoint结点
    # database.session.begin_nested()

    yield session

    # 默认未提交就回滚，所以感觉不需要写，但是为了体现事物完整性，还是加上
    # transaction.rollback()
    connection.close()
    session.remove()


# 添加一些文件配置到数据库中
@pytest.yield_fixture()
def default_settings(database):
    """创建默认的设置"""
    return None

