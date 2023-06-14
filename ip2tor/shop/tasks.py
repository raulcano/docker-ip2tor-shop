import subprocess
from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from charged.utils import add_change_log_entry, handle_obj_is_alive_change
from django.conf import settings
from django.utils import timezone
from django.core.management import call_command
from shop.models import Host, TorBridge

logger = get_task_logger(__name__)


class HostNotFoundError(Exception):
    pass


@shared_task()
def add(x, y):
    return x + y


@shared_task(ignore_result=True)
def update_metrics():
    TorBridge.update_metrics()


@shared_task()
def count_tor_bridges():
    return TorBridge.objects.count()


@shared_task(bind=True, ignore_result=True)
def host_alive_check(self, obj_id=None):
    if obj_id:
        hosts = Host.objects.filter(pk=obj_id)

        if not hosts[0]:
            logger.warning(f"Host not found: {obj_id}")
            raise HostNotFoundError
    else:
        hosts = Host.objects.filter(is_enabled=True)

    for host in hosts:
        alive = host.check_alive_status()

        if host.is_alive == alive:
            logger.debug(f"Host {host} *is_alive* status did not change - is still: {alive}")
            continue  # no change
        else:
            logger.debug(f"Host {host} *is_alive* status changed - is now: {alive}")
            handle_obj_is_alive_change(host, alive)


@shared_task()
def delete_due_tor_bridges():
    counter = 0
    deleted = TorBridge.objects.filter(status=TorBridge.NEEDS_DELETE)
    if deleted:
        for item in deleted:
            logger.debug('Running on: %s' % item)
            item.delete()
            counter += 1

    return f'Removed {counter}/{len(deleted)} Tor Bridge(s) from DB (previous state: NEEDS_DELETE).'


@shared_task()
def set_needs_delete_on_suspended_tor_bridges(days=getattr(settings, 'DELETE_SUSPENDED_AFTER_THESE_DAYS')):
    counter = 0
    suspended = TorBridge.objects.filter(status=TorBridge.SUSPENDED)
    if suspended:
        for item in suspended:
            logger.debug('Running on: %s' % item)
            if timezone.now() > item.modified_at + timedelta(days=days):
                logger.debug('Needs to be set to deleted.')
                item.status = TorBridge.NEEDS_DELETE
                item.save()
                add_change_log_entry(item, "set to NEEDS_DELETE")
                counter += 1

    return f'Set NEEDS_DELETE on {counter}/{len(suspended)} Tor Bridge(s) (previous state: SUSPENDED).'


@shared_task()
def set_needs_delete_on_initial_tor_bridges(minutes=getattr(settings, 'DELETE_INITIAL_AFTER_THESE_MINUTES')):
    counter = 0
    initials = TorBridge.objects.filter(status=TorBridge.INITIAL)
    if initials:
        for item in initials:
            logger.debug('Running on: %s' % item)
            if timezone.now() > item.modified_at + timedelta(minutes=minutes):
                logger.debug('Needs to be set to deleted.')
                item.status = TorBridge.NEEDS_DELETE
                item.save()
                add_change_log_entry(item, "set to NEEDS_DELETE")
                counter += 1

    return f'Set NEEDS_DELETE on {counter}/{len(initials)} Tor Bridge(s) (previous state: INITIAL).'


@shared_task()
def set_needs_suspend_on_expired_tor_bridges():
    counter = 0
    actives = TorBridge.objects.filter(status=TorBridge.ACTIVE)
    if actives:
        for item in actives:
            logger.info('Running on: %s' % item)

            if timezone.now() > item.suspend_after:
                logger.info('Needs to be suspended.')
                item.status = TorBridge.NEEDS_SUSPEND
                item.save()
                add_change_log_entry(item, "set to NEEDS_SUSPEND")
                counter += 1

    return f'Set NEEDS_SUSPEND on {counter}/{len(actives)} Tor Bridge(s) (previous state: ACTIVE).'


@shared_task()
def set_needs_bw_redirect_on_tor_bridges_with_no_bandwidth():
    counter = 0
    actives = TorBridge.objects.filter(status=TorBridge.ACTIVE)
    if actives:
        for item in actives:
            logger.info('Running on: %s' % item)

            if item.total_remaining_valid_bandwidth <= 0:
                logger.info('Needs to be redirected. Out of bandwidth.')
                item.status = TorBridge.NEEDS_BW_REDIRECT
                item.save()
                add_change_log_entry(item, "set to NEEDS_BW_REDIRECT")
                counter += 1

    return f'Set NEEDS_BW_REDIRECT on {counter}/{len(actives)} Tor Bridge(s) (previous state: ACTIVE).'


@shared_task()
def backup_files():
    subprocess.call(['sh',  settings.BASE_DIR + '/../scripts/backup-files.sh'])
    
@shared_task()
def delete_old_backups():
    subprocess.call(['bash',  settings.BASE_DIR + '/../scripts/delete-old-backups.sh'])

@shared_task()
def backup_db():
    call_command('dbbackup')