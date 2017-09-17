# -*- coding: utf-8 -*-
"""
    app.auth.views

    用户注册、认证视图层
"""
import StringIO
import os
import random
import string
import uuid

import datetime
from flask import g, current_app, url_for
from flask_restful import Resource, reqparse
from reportlab.lib.pagesizes import A4, A2, A3
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.platypus.flowables import PageBreak, Spacer
from reportlab.platypus.para import Paragraph

from app.extensions import db
from app.log_.constant import LogName
from app.log_.models import ComUserLog
from app.utils.database import model_to_dict
from app.utils.helpers import update_datetime
from app.utils.parser import common_parser
from app.utils.response import res_list_page, res
from app.utils.spreadsheettable import SpreadsheetTable

parser = reqparse.RequestParser()

# 添加通用参数解析
common_parser(parser)

styleSheet = getSampleStyleSheet()
MARGIN_SIZE = 25 * mm
PAGE_SIZE = A2
DEFAULT_PAGE_LENGTH = 86


def get_test_data(cols, rows):
    """
    Generates test data for Table objects.
    """
    assert cols > 0
    assert rows > 1

    data = [['Col %d' % col_num for col_num in xrange(cols)]]
    for row in xrange(rows - 1):
        row_data = [row * cols + col for col in xrange(cols)]
        data.append(row_data)

    return data


def __create_pdf_doc(pdfdoc, story):
    """
    Creates PDF doc from story.
    """
    pdf_doc = BaseDocTemplate(pdfdoc, title='航信云', author='TravelCloud',
                              subject='TravelCloud Log', creator='TravelCloud',
                              displayDocTitle=True, pagesize=PAGE_SIZE,
                              leftMargin=MARGIN_SIZE, rightMargin=MARGIN_SIZE,
                              topMargin=MARGIN_SIZE, bottomMargin=MARGIN_SIZE)
    main_frame = Frame(MARGIN_SIZE, MARGIN_SIZE,
                       PAGE_SIZE[0] - 2 * MARGIN_SIZE, PAGE_SIZE[1] - 2 * MARGIN_SIZE,
                       leftPadding=0, rightPadding=0, bottomPadding=0,
                       topPadding=0, id='main_frame')
    main_template = PageTemplate(id='main_template', frames=[main_frame])
    pdf_doc.addPageTemplates([main_template])

    pdf_doc.build(story)
    return pdf_doc


def _create_pdf(pdf_out, data):
    current_app.logger.info("开始创建pdf文件!")
    from reportlab.lib import colors
    import platform
    if "Linux" == platform.system():
        # linux下面支持文泉驿正黑
        pdfmetrics.registerFont(TTFont('hei', 'wqy-zenhei/wqy-zenhei.ttc'))
    elif "Windows" == platform.system():
        # windows下面使用微软雅黑
        current_app.logger.info("微软系统下面格式为ttc")
        pdfmetrics.registerFont(TTFont('hei', 'msyh.ttc'))
    table_style = [
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, -1), 'hei'),
    ]
    # 数据中插入标题列
    data.insert(0, [u"ID", u"操作人员", u"操作位置", u"操作时间", u"操作内容", u"操作结果"])
    story = []
    # 添加文件头部
    # title_style = styleSheet["Title"]
    # title_style.fontName = "hei"
    # story.append(Paragraph(u"航信云日志", styleSheet["Title"]))
    # story.append(Spacer(0, 10 * mm))
    data_length = len(data)
    for i in xrange(0, data_length, DEFAULT_PAGE_LENGTH):
        # if not i:
        #     story.append(Spacer(0, 10 * mm))
        #     story.append(Spacer(0, 10 * mm))
        spreadsheet_table = SpreadsheetTable(data[i: i + DEFAULT_PAGE_LENGTH - 1],
                                             colWidths=[50, 100, 125, 100, 450, 350], repeatRows=1)
        spreadsheet_table.setStyle(table_style)
        story.append(spreadsheet_table)
        story.append(PageBreak())

    return __create_pdf_doc(pdf_out, story)


def _get_table_data(keyword, q_type="base", page=1, per_page=1000, user_id=None, tenant_id=None):
    """
        songxiaowei 2017-2-15

        获取表中的数据
    """
    query = ComUserLog.query.with_entities(ComUserLog.id, ComUserLog.user_name, ComUserLog.place,
                                           ComUserLog.create_date, ComUserLog.operation, ComUserLog.result_msg)
    if user_id:
        query = query.filter(ComUserLog.user_id == user_id)

    if tenant_id:
        query = query.filter(ComUserLog.tenant_id == g.tenant.get("tenant_id"))

    # 超级管理员只能导出自己和匿名用户的日志
    if not (user_id and tenant_id):
        from sqlalchemy import or_
        query = query.filter(or_(ComUserLog.user_id == g.user.get("current_user_id"),
                                 ComUserLog.user_id == -1))
    if q_type == 'base':
        name = keyword.get("name", "")
        # query = query.filter(db.or_(ComUserLog.id.ilike("%{}%".format(name)),
        #                             ComUserLog.user_name.ilike("%{}%".format(name)),
        #                             ComUserLog.create_date.ilike("%{}%".format(name)),
        #                             ComUserLog.operation.ilike("%{}%".format(name)),
        #                             ComUserLog.result_msg.ilike("%{}%".format(name)),
        #                             ComUserLog.remark.ilike("%{}%".format(name)), ))
        query = query.filter(ComUserLog.user_name.ilike("%{}%".format(name)))

    elif q_type == 'advanced':
        if keyword.get("id"):
            # id_ = keyword.get("id")
            # if ',' in id_:
            #     ids = id_.split(',')
            # # 针对用户可能输入中文分隔符
            # elif '，' in id_:
            #     ids = id_.split('，')
            # else:
            #     ids = [id_]
            # ids.append(None)
            # query = query.filter(ComUserLog.id.in_(ids))
            query = query.filter(ComUserLog.id.ilike(keyword.get("id")))

        if keyword.get("opr_user"):
            query = query.filter(ComUserLog.user_name.ilike("%{}%".format(keyword["opr_user"])))

        if keyword.get("opr_datetime") and isinstance(keyword.get("opr_datetime"), list) and \
                keyword.get("opr_datetime")[0] and keyword.get("opr_datetime")[1]:
            try:
                keyword["opr_datetime"][1] = update_datetime(keyword["opr_datetime"][1], format_='%Y-%m-%d %H:%M')
            except Exception as e:
                current_app.logger.info(e)
                keyword["opr_datetime"][1] = update_datetime(keyword["opr_datetime"][1],
                                                             format_='%Y-%m-%d')
            query = query.filter(ComUserLog.create_date.between(*keyword["opr_datetime"]))
            # query = query.filter(ComUserLog.create_date.__ge__(keyword["opr_datetime"][0]),
            #                      ComUserLog.create_date.__le__(keyword["opr_datetime"][1]))

        if keyword.get("opr_place"):
            query = query.filter(ComUserLog.place.ilike("%{}%".format(keyword["opr_place"])))

        if keyword.get("operation"):
            query = query.filter(ComUserLog.operation.ilike("%{}%".format(keyword["operation"])))

        if keyword.get("operation_result"):
            query = query.filter(ComUserLog.result_msg.ilike("%{}%".format(keyword["operation_result"])))

        if keyword.get("remark"):
            query = query.filter(ComUserLog.remark.ilike("%{}%".format(keyword["remark"])))

    # 添加排序规则
    query = query.filter(ComUserLog.update_date.isnot(None)).order_by(ComUserLog.create_date.desc())
    data = query.paginate(page=page, per_page=per_page, error_out=False).items
    result = []
    for d in data:
        d = list(d)
        operation = d[4]
        from flask import json
        d[4] = ":".join([json.dumps(operation.get(v)) for v in
                         ("action", "resource_type", "id", "serial_number", "task_id") if operation.get(v, "")])
        result.append(d)

    return result


class AdminLogs(Resource):
    """
        songxiaowei 2017-2-14

        超级管理员视图下，列出所有的日志信息，默认时间倒序排列
    """

    @classmethod
    def post(cls):
        parser_get = parser.copy()
        args = parser_get.parse_args()
        # whfang 2017-04-05 超级管理员只能查自己和匿名用户的日志
        # query = ComUserLog.query
        from sqlalchemy import or_
        query = ComUserLog.query.filter(or_(ComUserLog.user_id == g.user.get("current_user_id"),
                                            ComUserLog.user_id == -1))
        if args.get("q_type") == 'base':
            name = args["keyword"].get("name", "")
            # query = query.filter(db.or_(ComUserLog.id.ilike("%{}%".format(name)),
            #                             ComUserLog.user_name.ilike("%{}%".format(name)),
            #                             ComUserLog.tenant_id.ilike("%{}%".format(name)),
            #                             ComUserLog.create_date.ilike("%{}%".format(name)),
            #                             ComUserLog.operation.ilike("%{}%".format(name)),
            #                             ComUserLog.result_msg.ilike("%{}%".format(name)),
            #                             ComUserLog.remark.ilike("%{}%".format(name)), ))
            query = query.filter(ComUserLog.user_name.ilike("%{}%".format(name)))

        elif args.get("q_type") == 'advanced':
            keyword_d = args["keyword"]
            if keyword_d.get("id"):
                # id_ = keyword_d.get("id")
                # if ',' in id_:
                #     ids = id_.split(',')
                # # 针对用户可能输入中文分隔符
                # elif '，' in id_:
                #     ids = id_.split('，')
                # else:
                #     ids = [id_]
                # ids.append(None)
                # query = query.filter(ComUserLog.id.in_(ids))
                query = query.filter(ComUserLog.id.ilike(keyword_d.get("id")))

            if keyword_d.get("opr_user"):
                query = query.filter(ComUserLog.user_name.ilike("%{}%".format(keyword_d["opr_user"])))

            if keyword_d.get("opr_tenant_id"):
                query = query.filter(ComUserLog.tenant_id.ilike("%{}%".format(keyword_d["opr_tenant_id"])))

            if keyword_d.get("opr_datetime") and isinstance(keyword_d.get("opr_datetime"), list) and \
                    keyword_d.get("opr_datetime")[0] and keyword_d.get("opr_datetime")[1]:
                try:
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d %H:%M')
                except Exception as e:
                    current_app.logger.info(e)
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d')
                query = query.filter(ComUserLog.create_date.between(*keyword_d["opr_datetime"]))

            if keyword_d.get("opr_place"):
                query = query.filter(ComUserLog.place.ilike("%{}%".format(keyword_d["opr_place"])))

            if keyword_d.get("operation"):
                query = query.filter(ComUserLog.operation.ilike("%{}%".format(keyword_d["operation"])))

            if keyword_d.get("operation_result"):
                query = query.filter(ComUserLog.result_msg.ilike("%{}%".format(keyword_d["operation_result"])))

            if keyword_d.get("remark"):
                query = query.filter(ComUserLog.remark.ilike("%{}%".format(keyword_d["remark"])))

        # 添加排序规则
        query = query.filter(ComUserLog.update_date.isnot(None)).order_by(ComUserLog.create_date.desc())
        data = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False).items
        count = query.count()
        return res_list_page(data=data, count=count, current_page=args["page"])


class AdminExportLogs(Resource):
    """
        songxiaowei 2017-2-15

        管理员视图下，导出当前用户所有的日志信息，默认时间倒序
    """

    @classmethod
    def post(cls):
        parser_post = parser.copy()
        parser_post.add_argument("per_page", type=int, default=10000, dest="per_page")
        args = parser_post.parse_args()
        # 生成随机文件名，避免重复
        # filename = "{}.pdf".format(str(uuid.uuid4()))
        filename = LogName.log_name()
        abs_path = os.path.join(current_app.root_path, "static", "pdf", filename)
        data = _get_table_data(keyword=args["keyword"], q_type=args["q_type"], page=args["page"],
                               per_page=args["per_page"])
        _create_pdf(abs_path, data=data)
        # response = make_response(pdf_out.getvalue())
        # response.headers['Content-Type'] = "application/pdf;charset=utf-8"
        # response.headers['mimetype'] = "application/pdf"
        # response.headers['Content-Disposition'] = "attachment; filename=logs.pdf;"
        # response.headers["Pragma"] = "No-cache"
        # response.headers["Cache-Control"] = "No-cache"
        # response.headers["Expires"] = 0
        return res(data={"filename": url_for("static", filename="pdf/{}".format(filename))})


class TenantLogs(Resource):
    """
        songxiaowei 2017-2-14

        租户视图下，列出当前租户下所有的日志信息，默认时间倒序排列
    """

    @classmethod
    def post(cls):
        parser_get = parser.copy()
        args = parser_get.parse_args()
        query = ComUserLog.query.filter(ComUserLog.tenant_id == g.tenant.get("tenant_id"))

        if args.get("q_type") == 'base':
            name = args["keyword"].get("name", "")
            # query = query.filter(db.or_(ComUserLog.id.ilike("%{}%".format(name)),
            #                             ComUserLog.user_name.ilike("%{}%".format(name)),
            #                             ComUserLog.create_date.ilike("%{}%".format(name)),
            #                             ComUserLog.operation.ilike("%{}%".format(name)),
            #                             ComUserLog.result_msg.ilike("%{}%".format(name)),
            #                             ComUserLog.remark.ilike("%{}%".format(name)), ))
            query = query.filter(ComUserLog.user_name.ilike("%{}%".format(name)))

        elif args.get("q_type") == 'advanced':
            keyword_d = args["keyword"]
            if keyword_d.get("id"):
                # id_ = keyword_d.get("id")
                # if ',' in id_:
                #     ids = id_.split(',')
                # # 针对用户可能输入中文分隔符
                # elif '，' in id_:
                #     ids = id_.split('，')
                # else:
                #     ids = [id_]
                # ids.append(None)
                # query = query.filter(ComUserLog.id.in_(ids))
                query = query.filter(ComUserLog.id.ilike(keyword_d.get("id")))

            if keyword_d.get("opr_user"):
                query = query.filter(ComUserLog.user_name.ilike("%{}%".format(keyword_d["opr_user"])))

            if keyword_d.get("opr_datetime") and isinstance(keyword_d.get("opr_datetime"), list) and \
                    keyword_d.get("opr_datetime")[0] and keyword_d.get("opr_datetime")[1]:
                try:
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d %H:%M')
                except Exception as e:
                    current_app.logger.info(e)
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d')
                query = query.filter(ComUserLog.create_date.between(*keyword_d["opr_datetime"]))

            if keyword_d.get("opr_place"):
                query = query.filter(ComUserLog.place.ilike("%{}%".format(keyword_d["opr_place"])))

            if keyword_d.get("operation"):
                query = query.filter(ComUserLog.operation.ilike("%{}%".format(keyword_d["operation"])))

            if keyword_d.get("operation_result"):
                query = query.filter(ComUserLog.result_msg.ilike("%{}%".format(keyword_d["operation_result"])))

            if keyword_d.get("remark"):
                query = query.filter(ComUserLog.remark.ilike("%{}%".format(keyword_d["remark"])))

        # 添加排序规则
        query = query.filter(ComUserLog.update_date.isnot(None)).order_by(ComUserLog.create_date.desc())
        data = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False).items
        count = query.count()
        return res_list_page(data=data, count=count, current_page=args["page"])


class TenantExportLogs(Resource):
    """
        songxiaowei 2017-2-15

        租户视图下，导出当前租户下所有的日志信息，默认时间倒序
    """

    @classmethod
    def post(cls):
        parser_post = parser.copy()
        parser_post.add_argument("per_page", type=int, default=10000, dest="per_page")
        args = parser_post.parse_args()
        # 生成随机文件名，避免重复
        # filename = "{}.pdf".format(str(uuid.uuid4()))
        filename = LogName.log_name()
        abs_path = os.path.join(current_app.root_path, "static", "pdf", filename)
        data = _get_table_data(keyword=args["keyword"], q_type=args["q_type"], page=args["page"],
                               per_page=args["per_page"], tenant_id=g.tenant.get("tenant_id"))
        _create_pdf(abs_path, data=data)
        return res(data={"filename": url_for("static", filename="pdf/{}".format(filename))})


class UserLogs(Resource):
    """
        songxiaowei 2017-2-14

        用户视图下，列出当前用户下所有的日志信息，默认时间倒序排列
    """

    @classmethod
    def post(cls):
        parser_get = parser.copy()
        args = parser_get.parse_args()
        query = ComUserLog.query.filter(ComUserLog.user_id == g.user.get("current_user_id"))

        if args.get("q_type") == 'base':
            name = args["keyword"].get("name", "")
            # query = query.filter(db.or_(ComUserLog.id.ilike("%{}%".format(name)),
            #                             ComUserLog.user_name.ilike("%{}%".format(name)),
            #                             ComUserLog.create_date.ilike("%{}%".format(name)),
            #                             ComUserLog.operation.ilike("%{}%".format(name)),
            #                             ComUserLog.result_msg.ilike("%{}%".format(name)),
            #                             ComUserLog.remark.ilike("%{}%".format(name)), ))
            query = query.filter(ComUserLog.user_name.ilike("%{}%".format(name)))

        elif args.get("q_type") == 'advanced':
            keyword_d = args["keyword"]
            if keyword_d.get("id"):
                # id_ = keyword_d.get("id")
                # if ',' in id_:
                #     ids = id_.split(',')
                # # 针对用户可能输入中文分隔符
                # elif '，' in id_:
                #     ids = id_.split('，')
                # else:
                #     ids = [id_]
                # ids.append(None)
                # query = query.filter(ComUserLog.id.in_(ids))
                query = query.filter(ComUserLog.id.ilike(keyword_d.get("id")))

            if keyword_d.get("opr_user"):
                query = query.filter(ComUserLog.user_name.ilike("%{}%".format(keyword_d["opr_user"])))

            if keyword_d.get("opr_datetime") and isinstance(keyword_d.get("opr_datetime"), list) and \
                    keyword_d.get("opr_datetime")[0] and keyword_d.get("opr_datetime")[1]:
                try:
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d %H:%M')
                except Exception as e:
                    current_app.logger.info(e)
                    keyword_d["opr_datetime"][1] = update_datetime(keyword_d["opr_datetime"][1],
                                                                   format_='%Y-%m-%d')

                query = query.filter(ComUserLog.create_date.between(*keyword_d["opr_datetime"]))

            if keyword_d.get("opr_place"):
                query = query.filter(ComUserLog.place.ilike("%{}%".format(keyword_d["opr_place"])))

            if keyword_d.get("operation"):
                query = query.filter(ComUserLog.operation.ilike("%{}%".format(keyword_d["operation"])))

            if keyword_d.get("operation_result"):
                query = query.filter(ComUserLog.result_msg.ilike("%{}%".format(keyword_d["operation_result"])))

            if keyword_d.get("remark"):
                query = query.filter(ComUserLog.remark.ilike("%{}%".format(keyword_d["remark"])))

        # 添加排序规则
        query = query.filter(ComUserLog.update_date.isnot(None)).order_by(ComUserLog.create_date.desc())
        data = query.paginate(page=args["page"], per_page=args["per_page"], error_out=False).items
        count = query.count()
        return res_list_page(data=data, count=count, current_page=args["page"])


class UserExportLogs(Resource):
    """
        songxiaowei 2017-2-16

        用户视图下，导出当前用户下所有的日志信息，默认时间倒序
    """

    @classmethod
    def post(cls):
        parser_post = parser.copy()
        parser_post.add_argument("per_page", type=int, default=10000, dest="per_page")
        args = parser_post.parse_args()
        # 生成随机文件名，避免重复
        # filename = "{}.pdf".format(str(uuid.uuid4()))
        filename = LogName.log_name()
        abs_path = os.path.join(current_app.root_path, "static", "pdf", filename)
        data = _get_table_data(keyword=args["keyword"], q_type=args["q_type"], page=args["page"],
                               per_page=args["per_page"], user_id=g.user.get("current_user_id"))
        _create_pdf(abs_path, data=data)
        return res(data={"filename": url_for("static", filename="pdf/{}".format(filename))})
