from django import forms

from .models import Player


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['phone_number']
