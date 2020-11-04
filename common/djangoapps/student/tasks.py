"""
This file contains celery tasks for sending email
"""
import logging

from boto.exception import NoAuthHandlerFound
from celery.exceptions import MaxRetriesExceededError
from celery.task import task  # pylint: disable=no-name-in-module, import-error
from crum import get_current_request
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse
from edx_ace import ace
from edx_ace.recipient import Recipient
from opaque_keys.edx.keys import CourseKey
from six import text_type

from openedx.core.djangoapps.ace_common.template_context import get_base_template_context
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.lib.celery.task_utils import emulate_http_request
from student.message_types import CourseEnrollment
from xmodule.modulestore.django import modulestore

log = logging.getLogger('edx.celery.task')


@task(bind=True)
def send_activation_email(self, subject, message, from_address, dest_addr):
    """
    Sending an activation email to the user.
    """
    max_retries = settings.RETRY_ACTIVATION_EMAIL_MAX_ATTEMPTS
    retries = self.request.retries
    try:
        mail.send_mail(subject, message, from_address, [dest_addr], fail_silently=False)
        # Log that the Activation Email has been sent to user without an exception
        log.info("Activation Email has been sent to User {user_email}".format(
            user_email=dest_addr
        ))
    except NoAuthHandlerFound:  # pylint: disable=broad-except
        log.info('Retrying sending email to user {dest_addr}, attempt # {attempt} of {max_attempts}'. format(
            dest_addr=dest_addr,
            attempt=retries,
            max_attempts=max_retries
        ))
        try:
            self.retry(countdown=settings.RETRY_ACTIVATION_EMAIL_TIMEOUT, max_retries=max_retries)
        except MaxRetriesExceededError:
            log.error(
                'Unable to send activation email to user from "%s" to "%s"',
                from_address,
                dest_addr,
                exc_info=True
            )
    except Exception:  # pylint: disable=bare-except
        log.exception(
            'Unable to send activation email to user from "%s" to "%s"',
            from_address,
            dest_addr,
            exc_info=True
        )
        raise Exception


@task(bind=True)
def send_course_enrollment_email_for_user(self, site_id, user_id, course_id):
    """
    Send out a course enrollment email for the given user.
    Arguments:
        site_id: Django Site object id
        user_id: Django User object id
        course_id: Course id
    """
    site = Site.objects.get(id=site_id)
    user = User.objects.get(id=user_id)
    with emulate_http_request(site=site, user=user):
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        request = get_current_request()
        message_context = get_base_template_context(site)
        message_context.update({
            'request': request,
            'platform_name': configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME),
            'site_name': configuration_helpers.get_value('SITE_NAME', settings.SITE_NAME),
            'full_name': user.get_full_name(),
            'course_name': course.display_name,
            'course_url': '{protocol}://{site}{link}'.format(
                protocol='https' if request.is_secure() else 'http',
                site=configuration_helpers.get_value('SITE_NAME', settings.SITE_NAME),
                link=reverse('course_root', kwargs={'course_id': course_id})
            ),
        })

        msg = CourseEnrollment().personalize(
            recipient=Recipient(user.username, user.email),
            language=preferences_api.get_user_preference(user, LANGUAGE_KEY),
            user_context=message_context,
        )
        ace.send(msg)
