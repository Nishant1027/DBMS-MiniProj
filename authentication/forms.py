from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .choices import ROLE_CHOICES



def invalid_username_validator(value):
    if '@' in value or '+' in value or '-' in value:
        raise ValidationError('Enter a valid username.')


def unique_email_validator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this Email already exists.')


def unique_username_ignore_case_validator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('User with this Username already exists.')


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'md-form-control'}),
        max_length=30,
        required=True,
        # help_text='Usernames may contain alphanumeric, _ and . characters'
        )  # noqa: E261
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'md-form-control'}),
        # help_text='Required. Inform a valid email address.',
        required=True,
        max_length=75)
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial='',
        widget=forms.Select(attrs={'class': 'md-form-control'}),
        required=True,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'md-form-control'}))
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'md-form-control'}),
        label="Confirm your password",
        required=True)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = ['username', 'email', 'role', 'password', 'confirm_password', ]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].validators.append(forbidden_usernames_validator)
        self.fields['username'].validators.append(invalid_username_validator)
        self.fields['username'].validators.append(
            unique_username_ignore_case_validator)
        self.fields['email'].validators.append(unique_email_validator)

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(
                ['Passwords don\'t match'])
        return self.cleaned_data
