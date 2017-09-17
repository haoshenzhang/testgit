from app.order.models import DisOrder
from app.utils.format import format_result
from app.cmdb.fw.models import CmdbFw
from flask import current_app
import json
from app.extensions import db

class FwCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = json.loads(order_info['apply_info'])
        CmdbFw.insert_fw_main(order_apply_info,order_id)
        db.session.commit()
        return True

class FwDeleteCMDB(object):
    def __init__(self):
        pass

    @staticmethod
    def update_cmdb(order_id):
        order_info = DisOrder.get_order_details(order_id)
        order_info = format_result(order_info)[0]
        order_apply_info = json.loads(order_info['apply_info'])
        CmdbFw.update_fw_main(order_apply_info['id'])
        db.session.commit()
        return True