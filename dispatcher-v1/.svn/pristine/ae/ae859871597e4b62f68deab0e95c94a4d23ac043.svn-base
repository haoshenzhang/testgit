# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask_restful import Api

from app.exceptions import errors
from app.management import management_app_bp
from app.management.image.views import ImageViewsApi, ImageEnvironmentApi, ImageTemplateApi, ImageOsApi, \
    ImageEnvironmentTemplateApi

image = Api(management_app_bp, prefix="/management/image", errors=errors)

# 添加rest资源
# 1.根据系统类型查镜像 2。新建镜像 3.发布取消发布 4.删除镜像
image.add_resource(ImageViewsApi, '/image')
# 查询环境,去除已经关联的环境
image.add_resource(ImageEnvironmentApi, '/image_environment')
# 1.查询环境对应的模板 2. 取消关联根据模板id和镜像id 3.关联镜像,如果已关联，不能再次关联
image.add_resource(ImageTemplateApi, '/image_template')
# 1.查询系统类型  2. 修改镜像名称
image.add_resource(ImageOsApi, '/image_os')
# 1.通过镜像id查询环境模板列表
image.add_resource(ImageEnvironmentTemplateApi, '/image_environment_template')