from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import render, redirect

from student.decorators import authentication_required
from student.forms import UserLoginForm, AddClassForm, SendFriendRequestForm
from student.forms import CreateAccountForm
from django.contrib.auth.models import User
from student.models import Student, FriendRequest, Friendship, Class, Enrollment
import datetime


@authentication_required
def home(request):
    if request.user is None:
        return redirect('login')
    # student = Student.objects.all().get(user=user)
    if request.method == 'POST':
        if 'send_friend_request' in request.POST:
            form = SendFriendRequestForm(request.POST)
            if form.is_valid():
                friend_username = form.cleaned_data.get('friend_username')
                if FriendRequest.objects.all().filter(sending_student=friend_username, receiving_student=request.user.username, request_status='A').exists() or FriendRequest.objects.all().filter(sending_student=request.user.username, receiving_student=friend_username, request_status='A').exists():
                    messages.error(request, 'You are already friends with this person!')
                    return redirect('home')
                if FriendRequest.objects.all().filter(sending_student=friend_username, receiving_student=request.user.username, request_status='U').exists():
                    messages.error(request, 'You may not send a friend request to this person because you have a pending friend request from them. To add them as a friend, accept the request that they have sent you.')
                    return redirect('home')
                if FriendRequest.objects.all().filter(sending_student=request.user.username, receiving_student=friend_username).exists(): # If friend req is rejected or unknown
                    messages.error(request, 'You have already sent this person a friend request before.')
                    return redirect('home')
                if request.user.username == friend_username:
                    messages.error(request, 'You cannot send friend requests to yourself')
                    return redirect('home')
                # friend = Student.objects.get(user=User.objects.get(username=friend_username))
                friend_does_exist = False
                for user in User.objects.all():
                    if user.username == friend_username:
                        friend_does_exist = True
                if friend_does_exist:
                    friend_request = FriendRequest(sending_student=request.user.username,
                                                   receiving_student=friend_username,
                                                   request_status='U')
                    friend_request.save()
                else:
                    messages.error(request, 'Friend does not exist')
                    return redirect('home')
            else:
                messages.error(request, 'Form is Invalid')
        elif 'accept_fr' in request.POST:
            friend_username = request.POST['accept_fr']
            friendship = Friendship(first_student_username=request.user.username,
                                    second_student_username=friend_username)
            friendship.save()
            fr = FriendRequest.objects.all().get(sending_student=friend_username,
                                                 receiving_student=request.user.username)
            fr.request_status = 'A'
            fr.save()
            return redirect('home')
        elif 'reject_fr' in request.POST:
            friend_username = request.POST['reject_fr']
            fr = FriendRequest.objects.all().get(sending_student=friend_username,
                                                 receiving_student=request.user.username)
            fr.request_status = 'R'
            fr.save()
            return redirect('home')
    unknown_friend_requests = FriendRequest.objects.all().filter(receiving_student=request.user.username,
                                                                 request_status='U')
    friendships = fetch_friendships(request.user.username)
    statuses = all_availability_statuses(friendships)
    available_friends = statuses[0]
    busy_friends = statuses[1]
    return render(request, 'student/home.html', {'unknown_friend_requests': unknown_friend_requests,
                                                 'friendships': friendships,
                                                 'friend_request_form': SendFriendRequestForm(),
                                                 'available_friends': available_friends,
                                                 'busy_friends': busy_friends})


def fetch_friendships(username):
    friends = []
    for friendship in Friendship.objects.all().filter(first_student_username=username):
        friends.append(friendship.second_student_username)
    for friendship in Friendship.objects.all().filter(second_student_username=username):
        friends.append(friendship.first_student_username)
    return friends


def all_availability_statuses(friendships):
    current_time = datetime.datetime.now()
    busy = []
    free = []
    for friend in friendships:
        student = Student.objects.get(user=User.objects.get(username=friend))
        enrollments = Enrollment.objects.all().filter(username=friend)
        klasses = []
        for enrollment in enrollments:
            klasses.append(Class.objects.all().filter(id=enrollment.class_id).first())
        added_to_busy = False
        for klass in klasses:
            if klass.start_time < current_time.time() < klass.end_time:
                busy.append(student)
                added_to_busy = True
                break
        if not added_to_busy:
            free.append(student)
    return free, busy


@authentication_required
def add_class(request):
    if request.method == 'POST':
        form = AddClassForm(request.POST)
        if form.is_valid():
            course_name = form.cleaned_data.get('course_name')
            teacher_first_name = form.cleaned_data.get('teacher_first_name')
            teacher_last_name = form.cleaned_data.get('teacher_last_name')
            days = form.cleaned_data.get('days')
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')

            if start_time == end_time:
                messages.error(request, 'Start time cannot be equal to end time.')
                return redirect('add_class')
            elif start_time > end_time:
                messages.error(request, 'Start time cannot be greater than end time.')
                return redirect('add_class')

            student_school = Student.objects.get(user=User.objects.get(username=request.user.username)).school

            for day in days:
                existing_klass = Class.objects.all().filter(course_name=course_name, teacher_first_name=teacher_first_name, teacher_last_name=teacher_last_name, day=day, start_time=start_time, end_time=end_time, school=student_school).first()
                if existing_klass is not None:
                    if has_already_enrolled(username=request.user.username, class_id=existing_klass.id):
                        messages.error(request, 'You have already enrolled for this class.')
                        return redirect('add_class')
                    enrollment = Enrollment(username=request.user.username, class_id=existing_klass.id)
                    enrollment.save()
                else:
                    klass = Class(course_name=course_name, teacher_first_name=teacher_first_name,
                                  teacher_last_name=teacher_last_name,
                                  day=day, start_time=start_time, end_time=end_time, school=student_school)
                    if has_already_enrolled(username=request.user.username, class_id=klass.id):
                        messages.error(request, 'You have already enrolled for this class.')
                        return redirect('add_class')
                    enrollment = Enrollment(username=request.user.username, class_id=klass.id)
                    klass.save()
                    enrollment.save()
            messages.success(request, 'Class Added Successfully.')
        else:
            messages.error(request, 'Form is Invalid')
    return render(request, 'student/add_class.html', {'form': AddClassForm()})


def has_already_enrolled(username, class_id):
    return Enrollment.objects.all().filter(username=username, class_id=class_id).exists()


@authentication_required
def remove_class(request):
    # if request.method == 'POST':
    #
    enrollments = Enrollment.objects.all().filter(username=request.user.username)
    klasses = []
    for enrollment in enrollments:
        klasses.append(Class.objects.all().get(id=enrollment.class_id))
    return render(request, 'student/remove_class.html', {'klasses': klasses})


# do we need authentication
def remove_a_class(request, klass_id):
    Enrollment.objects.all().get(class_id=klass_id, username=request.user.username).delete()
    return redirect('remove_class')


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid Username or Password')
        else:
            messages.error(request, 'Form is Invalid')
    return render(request, 'student/login.html', {'form': UserLoginForm()})


def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            school = form.cleaned_data.get('school')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            if password == confirm_password:
                user = User(username=username, email=email)
                user.set_password(password)
                student = Student(user=user, first_name=first_name, last_name=last_name, school=school)
                try:
                    user.save()
                    student.save()
                except():
                    return redirect('create_account')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match')
    return render(request, 'student/create_account.html', {'form': CreateAccountForm()})
