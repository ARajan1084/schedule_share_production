from django import forms

DAYS_OF_THE_WEEK = [(0, 'Sunday'),
                    (1, 'Monday'),
                    (2, 'Tuesday'),
                    (3, 'Wednesday'),
                    (4, 'Thursday'),
                    (5, 'Friday'),
                    (6, 'Saturday')]


class TimeInput(forms.TimeInput):
    input_type = 'time'


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CreateAccountForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    school = forms.CharField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class AddClassForm(forms.Form):
    course_name = forms.CharField()
    teacher_first_name = forms.CharField()
    teacher_last_name = forms.CharField()
    days = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=DAYS_OF_THE_WEEK)
    start_time = forms.TimeField(widget=TimeInput)
    end_time = forms.TimeField(widget=TimeInput)


class SendFriendRequestForm(forms.Form):
    friend_username = forms.CharField()
