# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.http import JsonResponse
from django.db.models import Q
from rest_framework.views import APIView

from student.models import User, EnrollmentBanned

class StudentAccessStatus(APIView):
    """
    Student status for access the courses in lms
    """

    def post(self, request):
        allowed_actions = ['ban', 'unban']
        action = request.data.get('action')

        if action not in allowed_actions:
            return JsonResponse({'message': 'Bad Action type'}, status=400)

        usernames_or_emails = re.split(r'[\n,]', request.data.get('identifiers'))
        usernames_or_emails = list(set([u.strip() for u in usernames_or_emails if u]))

        if action == 'ban':
            return self._set_student_all_ban_status(usernames_or_emails)

        elif action == 'unban':
            return self._remove_student_all_ban_status(usernames_or_emails)

    @staticmethod
    def _set_student_all_ban_status(usernames_or_emails):
        successful_usernames, invalid_usernames = [], []
        users = User.objects.filter(
            Q(email__in=usernames_or_emails) | Q(username__in=usernames_or_emails)
        )

        for user in users:
            student_provided_info = user.username if user.username in usernames_or_emails else user.email
            usernames_or_emails.remove(student_provided_info)

            banned_user, created = EnrollmentBanned.objects.get_or_create(email=user.email)

            if not created:
                banned_user.is_active = True
                banned_user.save(update_fields=['is_active'])

            successful_usernames.append({'identifier': student_provided_info, 'reason': ''})

        for raw_user in usernames_or_emails:
            if re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', raw_user):
                banned_user, created = EnrollmentBanned.objects.get_or_create(email=raw_user)
                banned_user.is_active = True
                banned_user.save(update_fields=['is_active'])
                successful_usernames.append({'identifier': raw_user, 'reason': ''})
            else:
                invalid_usernames.append(
                    {'identifier': raw_user, 'reason': 'username does not exist and cannot be added'})

        results = {
            'action': 'ban',
            'failed_results': invalid_usernames,
            'successful_results': successful_usernames
        }

        return JsonResponse(results)

    @staticmethod
    def _remove_student_all_ban_status(usernames_or_emails):
        successful_usernames, invalid_usernames = [], []
        registered_users_emails = User.objects.filter(
            Q(email__in=usernames_or_emails) | Q(username__in=usernames_or_emails)
        )

        registered_users_emails_values = registered_users_emails.values_list('email', flat=True)
        EnrollmentBanned.objects.filter(email__in=registered_users_emails_values).update(is_active=False)

        for user in registered_users_emails:
            student_provided_info = user.username if user.username in usernames_or_emails else user.email
            usernames_or_emails.remove(student_provided_info)
            successful_usernames.append({'identifier': student_provided_info, 'reason': ''})

        unregistered_emails = []

        for raw_user in usernames_or_emails:
            if re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$', raw_user):
                unregistered_emails.append(raw_user)
                successful_usernames.append({'identifier': raw_user, 'reason': ''})
            else:
                invalid_usernames.append(
                    {'identifier': raw_user, 'reason': 'username does not exist and cannot be added'}
                )

        EnrollmentBanned.objects.filter(email__in=unregistered_emails).update(is_active=False)

        results = {
            'action': 'unban',
            'failed_results': invalid_usernames,
            'successful_results': successful_usernames
        }

        return JsonResponse(results)
