from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.contrib.auth import get_user_model


class SignupForm(UserCreationForm):
    email = forms.EmailField(
        max_length=200,
        help_text='Required',
        validators=[validate_email],
        error_messages={
            'required': 'Please enter your email address',
            'invalid': 'Please enter a valid email address',
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
        error_messages = {
            'username': {
                'required': 'Please enter a username',
                'unique': 'This username is already taken'
            },
            'password2': {
                'required': 'Please confirm your password',
                'min_length': 'Your password must be at least 8 characters long',
                'common_password': 'Your password is too common',
                'numeric_password': 'Your password cannot be entirely numeric'
            }
        }


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
