from django import forms
from info.models import Users
import re

# Initiate logging
import logging
import outwithcorona.outwithcorona_logger # noqa
# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


class IdentificationForm(forms.ModelForm):
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={'name': 'phone_number'}
        )
    )
    county = forms.CharField(
        widget=forms.Select(attrs={'name': 'county'})
    )
    arrived_recently = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'arrived_recently'})
    )

    class Meta:
        model = Users

        fields = ['county', 'phone_number']
        exclude = ['verification_code']

    def clean(self, *args, **kwargs):
        logger.info('Executing identification form.')
        phone_number = self.cleaned_data.get('phone_number')
        valid_phone_number = re.search(r'7\d{8}$', phone_number)

        if valid_phone_number and len(phone_number) == 9:
            KE_CODE = "+254"
            phone_number = KE_CODE + phone_number

            self.cleaned_data['phone_number'] = phone_number
        else:
            self.add_error(
                'phone_number',
                'Please enter your phone number in the required format! Example: 706123456'
            )


class SymptomsForm(forms.Form):
    coughing_or_sneezing = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'coughing_or_sneezing'})
    )
    fever = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'fever'})
    )
    fatigue = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'fatigue'})
    )
    breathing_difficulty = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'breathing_difficulty'})
    )
    runny_nose = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'runny_nose'})
    )
    sore_throat = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'name': 'sore_throat'})
    )


class VerificationForm(forms.Form):
    verification_code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'name': 'verification_code'}
        )
    )
