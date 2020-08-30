from django import forms

from .models import Player


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["phone_number"]

    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].label = "Phone number (internation format only)"
        self.fields['phone_number'].widget.attrs.update({'placeholder': '+X-XXX-XXX-XXXX'})
