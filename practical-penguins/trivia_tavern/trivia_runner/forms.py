from django import forms
from django.db import models
from phonenumber_field.formfields import PhoneNumberField
from .models import PhoneNumber, ActiveTriviaQuiz


class PhoneNumberForm(forms.ModelForm):
    phone_number = PhoneNumberField()

    class Meta:
        model = PhoneNumber
        fields = ['phone_number']

class TimeoutForm(forms.Form):
    timeout = forms.IntegerField(min_value=30, max_value=180)
