#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import ConfigParser

from app.application import create_app
from app.extensions import celery

PY2 = sys.version_info[0] == 2

# 针对python2情况，设置默认编码为UTF-8
if PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')

# 部署环境配置, testing 测试环境, production 生产环境, development 开发环境
ini_config = ConfigParser.ConfigParser()
ini_config.readfp(open('uwsgi.ini'))
system_environments = ini_config.get("uwsgi", "system_environments")
if system_environments == "development":
    from app.configs.development import DevelopmentConfig as Config
elif system_environments == "production":
    from app.configs.production import ProductionConfig as Config
elif system_environments == "testing":
    from app.configs.testing import TestingConfig as Config

try:
    app = create_app(Config)
except Exception,e:
    print("启动错误，请检查uwsgi.ini配置")

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], threaded=True, passthrough_errors=True)
