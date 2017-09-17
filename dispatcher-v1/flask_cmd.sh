#!/usr/bin/env bash


function useage()
{
    echo "Usage:"
    echo "  sh flask_cmd.sh celery start user/bizs/network/infrastructure       启动celery任务"
    echo "  sh flask_cmd.sh celery stop  user/bizs/network/infrastructure       停止celery任务"
    echo "  sh flask_cmd.sh celery restart  user/bizs/network/infrastructure    重启celery任务"
    echo "  sh flask_cmd.sh uwsgi start                                         启动uwsgi"
    echo "  sh flask_cmd.sh uwsgi stop                                          停止uwsgi"
    echo "  sh flask_cmd.sh uwsgi restart                                       重启uwsgi"
    echo "  sh flask_cmd.sh crontab load port                                   加载crontab任务, port为项目启动端口"
    echo "  sh flask_cmd.sh crontab delete                                      删除crontab任务"
    echo "  sh flask_cmd.sh crontab start                                       启动crontab任务"
}

function cmd_3()
{
    if [ $1_ == "_" ]
    then
        echo "请输入正确的模块名 user/bizs/network/infrastructure"
        exit 1
    elif [ $1_ == "user_" ]
    then
        cmd3="email_task"
    elif [ $1_ == "bizs_" ]
    then
        cmd3="email_biz"
    elif [ $1_ == "network_" ]
    then
        cmd3="net_task"
    elif [ $1_ == "infrastructure_" ]
    then
        cmd3="inf_task"
    else
        echo "请输入正确的模块名 user/bizs/network/infrastructure"
        exit 1
    fi
}

function uwsgi_start()
{
    uwsgi $1/uwsgi.ini
    sleep 1
    ps aux | grep uwsgi | grep -v grep
    echo "Start UWSGI Done"
}

function uwsgi_stop()
{
    ps aux | grep uwsgi | grep -v grep | grep -v flask_cmd | awk '{print $2}' | xargs kill -9
    sleep 1
    ps aux | grep uwsgi | grep -v grep
    echo "Kill UWSGI Done"
}

function check_log_path()
{
    project_log_path_1="/opt"
    project_log_path_2="/opt/app"
    project_log_path_3="/opt/app/work"
    project_log_path_4="/opt/app/work/project_logs"
    if [ ! -d $project_log_path_1 ]
    then
        mkdir $project_log_path_1
        mkdir $project_log_path_2
        mkdir $project_log_path_3
        mkdir $project_log_path_4
    elif [ ! -d $project_log_path_2 ]
    then
        mkdir $project_log_path_2
        mkdir $project_log_path_3
        mkdir $project_log_path_4
    elif [ ! -d $project_log_path_3 ]
    then
        mkdir $project_log_path_3
        mkdir $project_log_path_4
    elif [ ! -d $project_log_path_4 ]
    then
        mkdir $project_log_path_4
    fi
}

function celery_start()
{
    export C_FORCE_ROOT=1
    if [ $1 == "inf_task" ]
    then
        nohup celery -A wsgi.celery  -B -l INFO -c 5 --maxtasksperchild=10 worker -Q $1 > $2/celery.log 2>&1 &
    else
        nohup celery -A wsgi.celery -l INFO -c 5 --maxtasksperchild=10 worker -Q email_task > $2/celery.log 2>&1 &
    fi
}

function celery_stop()
{
    ps aux | grep celery | grep $1 | grep -v grep | grep -v flask_cmd | awk '{print $2}' | xargs kill -9
    sleep 1
    ps aux | grep celery | grep $1
    echo "kill celery done"
}

function crontab_load()
{
    echo "01 00 * * * sh $1/flask_cmd.sh crontab start $2" > $1/crontab
    crontab $1/crontab
}

function crontab_delete()
{
    crontab -r
}

function crontab_start()
{
    time=`date "+%Y-%m-%d"`
    cp $1/uwsgi.$2.log $1/uwsgi.$2.$time.log
    cat /dev/null > $1/uwsgi.$1.log
}

project_log_path="/opt/app/work/project_logs/"
pwd_path=`pwd`
check_log_path
if [ $1_ == "_" ]
then
    useage
    exit 1
elif [ $1_ == "celery_" ]
then
    if [ $2 == "start" ]
    then
        cmd_3 $3
        celery_start $cmd3 $project_log_path
    elif [ $2 == "stop" ]
    then
        cmd_3 $3
        celery_stop $cmd3
    elif [ $2 == "restart" ]
    then
        cmd_3 $3
        celery_stop $cmd3
        celery_start $cmd3 $project_log_path
    fi
elif [ $1_ == "uwsgi_" -a $2 == "start" ]
then
    uwsgi_start $pwd_path
elif [ $1_ == "uwsgi_" -a $2 == "stop" ]
then
    uwsgi_stop
elif [ $1_ == "uwsgi_" -a $2 == "restart" ]
then
    uwsgi_stop
    uwsgi_start $pwd_path
elif [ $1_ == "crontab_" -a $2 == "load" ]
then
    crontab_load $pwd_path $3
elif [ $1_  == "crontab_" -a $2 == "delete" ]
then
    crontab_delete
elif [ $1_ == "crontab_" -a $2 == "start" ]
then
    crontab_start $project_log_path $3
else
    useage
    exit 1
fi
