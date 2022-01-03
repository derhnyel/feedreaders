from apscheduler.schedulers.background import BackgroundScheduler
from hackernews_engine import tasks
from datetime import datetime


def start():
    """Create BackgroundScheduler instance and run task on intervals"""
    scheduler = BackgroundScheduler(timezone="Asia/Beirut")
    now = datetime.now()
    scheduler.add_job(tasks.update_items,args=['top'],trigger="interval",minutes=5,id="FetchTopTaskid",replace_existing=True,misfire_grace_time=None,next_run_time=now)# add task to backgroud scheduler and run at intervals
    scheduler.add_job(tasks.update_items,args=['new'],trigger="interval",minutes=5,id="FetchNewTaskid",replace_existing=True,misfire_grace_time=None,next_run_time=now)# add task to backgroud scheduler and run at intervals
    scheduler.add_job(tasks.update_items,args=['job'],trigger="interval",minutes=20,id="FetchJobTaskid",replace_existing=True,misfire_grace_time=None,next_run_time=now)# add task to backgroud scheduler and run at intervals
    scheduler.start()