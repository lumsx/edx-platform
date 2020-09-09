from django.contrib import admin

from openedx.features.course_rating import models


@admin.register(models.CourseRatings)
class CourseRatingsAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'course_id',
        'course_rating',
    ]


@admin.register(models.CourseRatingQuestions)
class CourseRatingQuestionsAdmin(admin.ModelAdmin):
    list_display = [
        'course_id',
        'question',
    ]


@admin.register(models.CourseRatingAnswers)
class CourseRatingAnswersAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'course_id',
        'question_id',
        'answer',
    ]


@admin.register(models.CourseRatingOverview)
class CourseRatingOverviewAdmin(admin.ModelAdmin):
    list_display = [
        'course_id',
        'overall_rating',
        'rating_count',
    ]
