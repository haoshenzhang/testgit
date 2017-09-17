# -*- coding: utf-8 -*-
"""
    app.auth.views

    用户注册、认证视图层
"""
from flask import current_app

from app.auth import auth_app_bp
from app.auth.models import ComTempInfo
from app.auth.schema import input_json_schema3, input_json_schema
from app.utils.database import new_session
from app.utils.email_ import send_email
from app.utils.my_logger import ActionType, ResourceType, log_decorator
from app.utils.parser import validate_schema, common_parser
from app.utils.response import res


@auth_app_bp.route("/test/<id_>", methods=["GET", "POST", "DELETE"])
@log_decorator(action=ActionType.create.value, resource=ResourceType.vpc.value)
def test(id_):
    """
    sxw 2016-12-7

    测试开启事务和会话功能
    """
    # with new_session() as session:
    #     result = session.query(ComTempInfo).all()
    #
    # return res(data=result)
    current_app.logger.warning("Hello world!", exc_info=False)
    # try:
    #     5 / 0
    # except Exception as e:
    #     current_app.logger.error("除数不能为0!", exc_info=True)
    return res(data={"serial_number": "fdasfadsfads2432432"})


@auth_app_bp.route("/test-json", methods=["POST"])
# @validate_schema(input_json_schema)
# @validate_schema(input_json_schema2)
def test_json():
    """
    sxw 2016-12-7

    测试开启事务和会话功能
    """
    # from flask import request
    # result = request.json
    # print request.json

    from flask_restful import reqparse
    parser = reqparse.RequestParser()

    # 添加通用参数解析
    common_parser(parser)

    parser_post = parser.copy()
    result = parser_post.parse_args()
    print result
    # with new_session() as session:
    #     result = session.query(ComTempInfo).all()

    return res(data=result)


@auth_app_bp.route("/test-celery")
def test_celery():
    from app import tasks
    tasks.select_temp()
    return res()
