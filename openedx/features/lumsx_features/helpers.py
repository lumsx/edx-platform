from openedx.core.djangoapps.theming.helpers import get_current_site
from openedx.features.lumsx_features.tasks import send_course_enrollment_email_for_user


def handle_course_enrollment(course_id, user, message_type):
    """
    Handle the course enrollment and send the email to the student about enrollment.
    Arguments:
        course_id: id of course in which user enrolled
        user: User enrolled in course
        message_type: 'enroll' or 'unenroll'
    """
    site = get_current_site()
    site_id = site.id if site else ''

    send_course_enrollment_email_for_user.delay(site_id, user.id, str(course_id), message_type)
