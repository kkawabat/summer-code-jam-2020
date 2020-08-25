from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Player
from phonenumber_field.phonenumber import PhoneNumber


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["phone_number"]

    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].label = "Phone number (internation format only)"
        self.fields['phone_number'].widget.attrs.update({'placeholder': '+X-XXX-XXX-XXXX'})

