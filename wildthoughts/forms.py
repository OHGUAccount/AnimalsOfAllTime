from django import forms
from django.contrib.auth.models import User
from wildthoughts.models import UserProfile,Animal,Discussion,Comment,UserList

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        fields = ('username', 'email','password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('webiste', 'picture')
