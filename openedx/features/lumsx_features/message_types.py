"""
ACE message types for the lumsx_feature.
"""

from openedx.core.djangoapps.ace_common.message import BaseMessageType


class CourseEnrollment(BaseMessageType):
    """
    A message for _registered_ learners who have been enrolled to a course.
    """
    APP_LABEL = 'lumsx_features'

    def __init__(self, *args, **kwargs):
        super(CourseEnrollment, self).__init__(*args, **kwargs)
        self.options['transactional'] = True  # pylint: disable=unsupported-assignment-operation


class CourseUnenrollment(BaseMessageType):
    """
    A message for _registered_ learners who have been unenrolled from a course.
    """
    APP_LABEL = 'lumsx_features'

    def __init__(self, *args, **kwargs):
        super(CourseUnenrollment, self).__init__(*args, **kwargs)
        self.options['transactional'] = True  # pylint: disable=unsupported-assignment-operation
