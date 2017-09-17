# !/usr/bin/python
# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler
from app.deployment.models import ComAsyncTask
from apscheduler.events import EVENT_JOB_ERROR,EVENT_JOB_EXECUTED


back_ground_scheduler = BackgroundScheduler()


def new_async_task(item_id,com_async_task_id,order_id,ctx):
    back_ground_scheduler.add_job(get_work_status, 'interval',id=item_id, seconds=20, jobstore='test_sch',
                                          args=[item_id,com_async_task_id,order_id,ctx])
    back_ground_scheduler.add_listener(task_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

def task_listener(event):
    if event.exception:
        print 'crash',event.exception
    else:
        print 'work'

def get_work_status(job_id,com_async_task_id,order_id,ctx):
    """
    查询执行状态（需要重载）
    :return:
    """

    job_id = str(job_id)

    print 'polling!!!!!!!!!!!'
    ctx.push()
    async_task_info = ComAsyncTask.get_async_task_status(order_id,com_async_task_id)

    if async_task_info['code'] == 1:
        print 'remove'
        back_ground_scheduler.remove_job(job_id=job_id, jobstore='test_sch')
        #TaskService.update_task() #回调task