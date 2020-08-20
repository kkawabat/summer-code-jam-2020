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
        self.fields['phone_number'].label = "Phone number* (US domestic or internation format only)"

    def clean_phone_number(self):
        """
        try to ensure the phone number is valid, if not try assume it's in US format, if user input is invalid
        if that fails raise ValidationError
        """
        phone_number = self.cleaned_data['phone_number']
        if PhoneNumber.from_string(phone_number).is_valid():
            return phone_number
        else:
            us_phone_number = PhoneNumber.from_string(phone_number, region="us")
            if us_phone_number.is_valid():
                return str(us_phone_number)
            else:
                raise ValidationError(f"phone number not valid use +XXXXXXXXXXX format", code='invalid')
