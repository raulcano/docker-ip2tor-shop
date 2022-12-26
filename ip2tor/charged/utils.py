from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.admin.options import get_content_type_for_model
from django.core.mail import EmailMessage
from io import BytesIO
import pycurl
import importlib


class MailNotificationToOwnerError(Exception):
    """E-Mail notification to owner raise an error"""
    pass

def dynamic_import_class(module_name, class_name):
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def create_email_message(subject: str, body: str, recipients: list,
                         from_email: str = None,
                         reference_tag: str = None):
    if from_email is None:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')

    if reference_tag:
        msg = EmailMessage(
            subject, body, from_email, recipients,
            headers={'References': f'<{reference_tag}/{from_email}>'}
        )
    else:
        msg = EmailMessage(subject, body, from_email, recipients)
    return msg


def handle_obj_is_alive_change(obj, new_status):
    LogEntry.objects.log_action(
        user_id=1,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message="Task: Check_alive -> set is_alive=%s" % new_status,
    )

    if new_status:
        obj.is_alive = True
        obj.save()
    else:
        obj.is_alive = False
        obj.save()

    if obj.owner.email:
        try:
            msg = create_email_message(f'[IP2Tor] {obj.__class__.__name__} status change: {obj.name}',
                                       f'{obj} - is_alive now: {new_status}',
                                       [obj.owner.email],
                                       reference_tag=f'{obj.__class__.__name__.lower()}/{obj.id}')
            msg.send()

        except Exception:
            raise MailNotificationToOwnerError


def add_change_log_entry(obj, message: str, user_id=1):
    LogEntry.objects.log_action(
        user_id=user_id,
        content_type_id=get_content_type_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=CHANGE,
        change_message=message,
    )

def ensure_https(url):
    if not url.startswith('https://'):
        return False

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.PROXY, 'socks5h://localhost:9050')
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.SSL_VERIFYHOST, False)
    c.setopt(c.SSL_VERIFYPEER, False)

    try:
        c.perform()
        # HTTP response code, e.g. 200.
        # print('Status: %d' % c.getinfo(c.RESPONSE_CODE))
        return True

    except pycurl.error as err:
        print(f"Exception: {err}")
        return False

    finally:
        c.close()


def is_onion(url):
    return url.endswith('.onion')