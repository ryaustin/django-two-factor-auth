import re

import phonenumbers
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from two_factor.plugins.registry import MethodNotFoundError, registry

phone_mask = re.compile(r'(?<=.{3})[0-9](?=.{2})')


def backup_phones(user):
    no_gateways = (
        getattr(settings, 'TWO_FACTOR_CALL_GATEWAY', None) is None
        and getattr(settings, 'TWO_FACTOR_WHATSAPP_GATEWAY', None) is None
        and getattr(settings, 'TWO_FACTOR_SMS_GATEWAY', None) is None)
    no_user = not user or user.is_anonymous

    if no_gateways or no_user:
        from .models import PhoneDevice
        return PhoneDevice.objects.none()
    return user.phonedevice_set.filter(name='backup')


def get_available_phone_methods():
    methods = []
    if getattr(settings, 'TWO_FACTOR_CALL_GATEWAY', None):
        methods.append(('call', _('Phone call')))
    if getattr(settings, 'TWO_FACTOR_SMS_GATEWAY', None):
        methods.append(('sms', _('Text message')))
    if getattr(settings, 'TWO_FACTOR_WHATSAPP_GATEWAY', None):
        methods.append(('whatsapp', _('WhatsApp message')))
    return methods


def backup_phones(user):
    if not user or user.is_anonymous:
        return []

    phones = []
    for method_name, _ in get_available_phone_methods():
        try:
            method = registry.get_method(method_name)  # Fetch method object
            phones += list(method.get_devices(user))
        except MethodNotFoundError:
            # Handle missing method gracefully
            continue

    return [phone for phone in phones if phone.name == 'backup']


def mask_phone_number(number):
    """
    Masks a phone number, only first 3 and last 2 digits visible.

    Examples:

    * `+31 * ******58`

    :param number: str or phonenumber object
    :return: str
    """
    if isinstance(number, phonenumbers.PhoneNumber):
        number = format_phone_number(number)
    return phone_mask.sub('*', number)


def format_phone_number(number):
    """
    Formats a phone number in international notation.
    :param number: str or phonenumber object
    :return: str
    """
    if not isinstance(number, phonenumbers.PhoneNumber):
        number = phonenumbers.parse(number)
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
