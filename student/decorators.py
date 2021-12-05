import uuid

from django.shortcuts import redirect

from .models import Student


def authentication_required(function):
    def wrapper(request, *args, **kwargs):
        user = request.user
        try:
            student = Student.objects.all().get(user=user)
        except:
            return redirect('login')
        return function(request, *args, **kwargs)

    return wrapper
