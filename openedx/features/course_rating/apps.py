from __future__ import unicode_literals

from django.apps import AppConfig


class CourseRatingConfig(AppConfig):
    name = 'openedx.features.course_rating'

    def ready(self):
        super(CourseRatingConfig, self).ready()
