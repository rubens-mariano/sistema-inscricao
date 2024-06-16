from django.conf import settings
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from apps.inscricao.models import SelecaoTemporaria


def limpar_dados_temporarios_inscricao():
    SelecaoTemporaria.clean_expired_selections()
    print('Executou!')


@util.close_old_connections
def delete_old_job_executions(max_age=172_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")

scheduler.add_job(
    limpar_dados_temporarios_inscricao,
    trigger=CronTrigger(minute="*/5"),
    id="limpar_dados_temporarios_inscricao",
    max_instances=1,
    replace_existing=True,
)

scheduler.add_job(
    delete_old_job_executions,
    trigger=CronTrigger(minute="*/6"),
    id="delete_old_job_executions",
    max_instances=1,
    replace_existing=True,
)

try:
    scheduler.start()
except KeyboardInterrupt:
    scheduler.shutdown()

