from celery.task import task  # pylint: disable=no-name-in-module, import-error
from crum import get_current_request
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.urls import reverse
from edx_ace import ace
from edx_ace.recipient import Recipient
from opaque_keys.edx.keys import CourseKey

from openedx.core.djangoapps.ace_common.template_context import get_base_template_context
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api.preferences import api as preferences_api
from openedx.core.lib.celery.task_utils import emulate_http_request
from openedx.features.lumsx_features.message_types import CourseEnrollment, CourseUnenrollment
from xmodule.modulestore.django import modulestore


@task(bind=True)
def send_course_enrollment_email_for_user(self, site_id, user_id, course_id, message_type):
    """
    Send out a course enrollment email for the given user.
    Arguments:
        site_id: Django Site object id
        user_id: Django User object id
        course_id: Course id
        message_type: 'enroll' or 'unenroll'
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
            'username': user.username,
            'course_name': course.display_name,
            'course_url': '{protocol}://{site}{link}'.format(
                protocol='https' if request.is_secure() else 'http',
                site=configuration_helpers.get_value('SITE_NAME', settings.SITE_NAME),
                link=reverse('course_root', kwargs={'course_id': course_id})
            ),
        })

        ace_messages_dict = {
            'enroll': CourseEnrollment,
            'unenroll': CourseUnenrollment,
        }
        message_class = ace_messages_dict[message_type]
        msg = message_class().personalize(
            recipient=Recipient(user.username, user.email),
            language=preferences_api.get_user_preference(user, LANGUAGE_KEY),
            user_context=message_context,
        )
        ace.send(msg)
