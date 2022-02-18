from datetime import datetime
from pyexpat.errors import messages
from urllib import request
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, resolve_url
from django.utils.functional import lazy
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView
from django_otp import devices_for_user
from django_otp.decorators import otp_required

from ..forms import DisableForm
from ..models import get_available_phone_methods
from ..utils import backup_phones, default_device
from .utils import class_view_decorator

from sendgrid.helpers.mail.mail import Mail
from payroll_web.utils import get_company, send_email
from archipay.settings import base as site_settings


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class ProfileView(TemplateView):
    """
    View used by users for managing two-factor configuration.

    This view shows whether two-factor has been configured for the user's
    account. If two-factor is enabled, it also lists the primary verification
    method and backup verification methods.
    """
    template_name = 'two_factor/profile/profile.html'

    def get_context_data(self, **kwargs):
        try:
            backup_tokens = self.request.user.staticdevice_set.all()[0].token_set.count()
        except Exception:
            backup_tokens = 0
        
        company = get_company(self.request)
        allow_disable_two_factor = company.allow_disable_two_factor
        return {
            'default_device': default_device(self.request.user),
            'default_device_type': default_device(self.request.user).__class__.__name__,
            'backup_phones': backup_phones(self.request.user),
            'backup_tokens': backup_tokens,
            'available_phone_methods': get_available_phone_methods(),
            'allow_disable_two_factor' : allow_disable_two_factor,
        }


@class_view_decorator(never_cache)
class DisableView(FormView):
    """
    View for disabling two-factor for a user's account.
    """

    # def allowed(self, *args, **kwargs):
    #     company = get_company(self.request)
    #     if not company.allow_disable_two_factor:
    #         error_message = f"{company.name} does not allow 2FA to be disabled. Please send an authorized email request to info@thepayroll.app"
    #         messages.error(self.request, error_message)
    #         return redirect('two_factor:profile')

    template_name = 'two_factor/profile/disable.html'
    success_url = lazy(resolve_url, str)(settings.LOGIN_REDIRECT_URL)
    form_class = DisableForm

    def dispatch(self, *args, **kwargs):
        # We call otp_required here because we want to use self.success_url as
        # the login_url. Using it as a class decorator would make it difficult
        # for users who wish to override this property

        company = get_company(self.request)
        if not company.allow_disable_two_factor:
            error_message = f"{company.name} does not allow 2FA to be disabled. Please send an authorized email request to info@thepayroll.app"
            messages.error(self.request, error_message)
            return redirect('two_factor:profile')

        fn = otp_required(super().dispatch, login_url=self.success_url, redirect_field_name=None)
        return fn(*args, **kwargs)

    def form_valid(self, form):
        # Ryan adding settings here to disallow disabling of 2FA
        company = get_company(self.request)
        if not company.allow_disable_two_factor:
            error_message = f"{company.name} does not allow 2FA to be disabled. Please send an authorized email request to info@thepayroll.app"
            messages.error(self.request, error_message)
            return redirect('two_factor:profile')

        for device in devices_for_user(self.request.user):
            device.delete()
        
        company = get_company(self.request)
        now = datetime.now().strftime('%d-%B-%Y %H:%M')
        email_message = Mail(
            from_email = site_settings.DEFAULT_FROM_EMAIL,
            to_emails= company.email if company.email else request.user.email,
            subject= 'WARNING: Two-Factor Authentication Disabled',
            html_content=(
                f'<p>Hi { company.primary_contact_name } two factor authentication was disabled on your The Payroll App account by {self.request.user} at {now}.</p>'

                f'Please contact {site_settings.ADMIN_EMAIL} if you suspect malicious or fraudlent activity.'
                )
            )
        email_notification_message = f"Two-Factor Authentication disabled and notication email sent"
        send_email(email_message=email_message, 
                notification_message=email_notification_message,
                request=self.request)
        logout(self.request)
            
        return redirect(self.success_url)
