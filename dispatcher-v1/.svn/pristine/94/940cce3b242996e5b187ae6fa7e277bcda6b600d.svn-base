# !/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.restful import Api

from app.catalog import catalog_app_bp
from app.exceptions import errors
from app.catalog.operation_monitoring.views import TrusteeshipYesApi, TrusteeshipNoApi

trusteeship = Api(catalog_app_bp, prefix="/catalog/trusteeship", errors=errors)

trusteeship.add_resource(TrusteeshipYesApi, '/yes')
trusteeship.add_resource(TrusteeshipNoApi, '/no')