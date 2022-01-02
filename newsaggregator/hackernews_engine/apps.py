from django.apps import AppConfig


class HackernewsEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hackernews_engine'
    # def ready(self):
    #     """This method is called when the application starts running"""
    #     print("Starting Scheduler...")
    #     from hackernews_engine.scheduler import hnapi_scheduler 
    #     hnapi_scheduler.start()
