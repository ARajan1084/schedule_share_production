import uuid

from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=30, unique=False, null=False)
    last_name = models.CharField(max_length=50, unique=False, null=False)
    school = models.CharField(max_length=50, unique=False, null=False)

    class Meta:
        db_table = 'students'


class Class(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, null=False)
    course_name = models.CharField(max_length=50, unique=False, null=False)
    teacher_first_name = models.CharField(max_length=30, unique=False, null=False)
    teacher_last_name = models.CharField(max_length=50, unique=False, null=False)
    # sunday = 0
    day = models.IntegerField(unique=False, null=False)
    start_time = models.TimeField(unique=False, null=False)
    end_time = models.TimeField(unique=False, null=False)
    school = models.CharField(max_length=50, unique=False, null=False)

    class Meta:
        db_table = 'classes'


class Friendship(models.Model):
    # student can have multiple Friendships, and each Friendship involves multiple (specifically: 2) students
    first_student_username = models.CharField(max_length=10, unique=False, null=False)
    second_student_username = models.CharField(max_length=10, unique=False, null=False)

    class Meta:
        db_table = 'friendships'


class FriendRequest(models.Model):
    # student can have multiple FriendRequests, but each individual FriendRequest is specific to one student
    sending_student = models.CharField(max_length=10, unique=False, null=False)
    receiving_student = models.CharField(max_length=10, unique=False, null=False)
    # U = unknown, A = accept, R = reject
    request_status = models.CharField(max_length=1, default='U', unique=False, null=False)

    class Meta:
        db_table = "friend requests"


class Enrollment(models.Model):
    username = models.CharField(max_length=10, unique=False, null=False)
    class_id = models.UUIDField(default=uuid.uuid4, primary_key=False, unique=False, null=False)

    class Meta:
        db_table = "enrollments"
