from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def validate_host_name_no_underscore(value):
    if '_' in value:
        raise ValidationError(_('Underscores are not allowed.'))


def validate_host_name_blacklist(value):
    blacklist = ['www', 'shop']
    if value in blacklist:
        raise ValidationError(
            _('Must not be one of: %(blacklist)s'),
            params={'blacklist': ', '.join(blacklist)},
        )


def validate_target_is_onion(value):
    if '.onion:' not in value:
        raise ValidationError(_('Must be an .onion address followed by a port.'))


def validate_target_has_port(value):
    s = value.split(':')
    try:
        p = s[-1]
        int(p)
    except (IndexError, ValueError):
        raise ValidationError(_('Must include a port as last part.'))

def validate_nostr_alias_blacklist(value):
    blacklist = getattr(settings, 'NOSTR_ALIAS_BLACKLIST')
    if value in blacklist:
        raise ValidationError(
            _('The selected alias is taken. Try another one...')
        )

def validate_alias_unique_in_ip(value):
    # ToDo
    
    # for nostr_alias in NostrAlias.objects.filter(alias__iexact=clean_alias):
    #                     if nostr_alias.host.ip == host.ip:
    #                         host_id = request.POST.get(submitted_product_type + 'Host_id')
    #                         errors.append('This alias is already taken. Please try another one...')
    #                         break
    pass


def validate_nostr_pubkey(value):
    pass
