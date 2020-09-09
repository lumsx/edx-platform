"""
Django Model for Course-Rating
"""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


UserModel = get_user_model()


class CourseRatings(models.Model):
    user_id = models.ForeignKey(
        UserModel,
        related_name='course_ratings',
        on_delete=models.CASCADE,
    )
    course_id = models.ForeignKey(
        CourseOverview,
        related_name='course_ratings',
        on_delete=models.CASCADE,
    )
    course_rating = models.IntegerField(
        default=5,
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    class Meta(object):
        unique_together = ['user_id', 'course_id']


class CourseRatingQuestions(models.Model):
    course_id = models.ForeignKey(
        CourseOverview,
        related_name='course_rating_questions',
        on_delete=models.CASCADE,
    )
    question = models.TextField(
        null=False,
        blank=False,
    )


class CourseRatingAnswers(models.Model):
    user_id = models.ForeignKey(
        UserModel,
        related_name='course_rating_answers',
        on_delete=models.CASCADE,
    )
    course_id = models.ForeignKey(
        CourseOverview,
        related_name='course_rating_answers',
        on_delete=models.CASCADE,
    )
    question_id = models.ForeignKey(
        CourseRatingQuestions,
        related_name='course_rating_answers',
        on_delete=models.CASCADE,
    )
    answer = models.TextField(
        null=False,
        blank=False,
    )

    class Meta(object):
        unique_together = ['user_id', 'course_id', 'question_id']


class CourseRatingOverview(models.Model):
    course_id = models.OneToOneField(
        CourseOverview,
        related_name='course_rating_overview',
        on_delete=models.CASCADE,
    )
    overall_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    rating_count = models.IntegerField(
        default=0,
    )
