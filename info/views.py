from django.shortcuts import render
from django.http import HttpRequest
from info.forms import IdentificationForm, SymptomsForm, VerificationForm
from django.shortcuts import redirect
from info.models import Users, CoronaSymptoms
from info.tasks import send_verification_code, get_county_population
from info.data_choices import (
    COUNTY_CHOICES, COUGHING_OR_SNEEZING, FATIGUE,
    RUNNY_NOSE, BREATHING_DIFFICULTY, FEVER, SORE_THROAT
)
from datetime import date
import math

# Initiate logging
import logging
import outwithcorona.outwithcorona_logger # noqa
# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


# Create your views here.
def identification(request, exception=None):
    """ Handles the identification page and any errors"""
    assert isinstance(request, HttpRequest)
    logger.info('Rendering identification page.')

    counties_list = []

    for county in COUNTY_CHOICES:
        counties_list.append(county[0])

    identification_form = IdentificationForm(request.POST or None)

    if identification_form.is_valid():
        logger.info('Identification form is valid')
        phone_number = identification_form.cleaned_data.get('phone_number')

        county = identification_form.cleaned_data.get('county')
        arrived_recently = identification_form.cleaned_data.get('arrived_recently')

        request.session['county'] = str(county)
        request.session['phone_number'] = str(phone_number)

        phone_number_qs = Users.objects.filter(phone_number=phone_number)
        if not phone_number_qs.exists():
            Users.objects.create(
                phone_number=phone_number,
                county=county,
                arrived_recently=arrived_recently
            )
            logger.info('{} successfull registration'.format(phone_number))
        else:
            Users.objects.filter(phone_number=phone_number).update(
                phone_number=phone_number,
                county=county,
                arrived_recently=arrived_recently
            )
            logger.info('{}: return user successfull update'.format(phone_number))

        return redirect(get_symptoms)

    return render(
        request,
        'info/details.html',
        {
            'title': 'Details',
            'form': identification_form,
            'counties': counties_list
        }
    )


def get_symptoms(request):
    """ Handles the symptoms page"""
    assert isinstance(request, HttpRequest)
    logger.info('Rendering get_symptoms page.')

    symptoms_form = SymptomsForm(request.POST or None)

    if symptoms_form.is_valid():
        logger.info('Symptoms form is valid')
        user = Users.objects.get(phone_number=request.session['phone_number'])
        symptoms = []

        if symptoms_form.cleaned_data.get('coughing_or_sneezing'):
            symptoms.append(COUGHING_OR_SNEEZING)

        if symptoms_form.cleaned_data.get('fever'):
            symptoms.append(FEVER)

        if symptoms_form.cleaned_data.get('fatigue'):
            symptoms.append(FATIGUE)

        if symptoms_form.cleaned_data.get('breathing_difficulty'):
            symptoms.append(BREATHING_DIFFICULTY)

        if symptoms_form.cleaned_data.get('runny_nose'):
            symptoms.append(RUNNY_NOSE)

        if symptoms_form.cleaned_data.get('sore_throat'):
            symptoms.append(SORE_THROAT)

        user_status_qs = CoronaSymptoms.objects.filter(user=user)

        if not user_status_qs.exists():
            logger.info('{} creating user symptoms'.format(request.session['phone_number']))
            CoronaSymptoms.objects.create(
                user=user,
                user_symptoms=symptoms
            )
        else:
            user_status = CoronaSymptoms.objects.get(user=user)

            user_status.user_symptoms = symptoms
            user_status.save()
            logger.info('{} updated user symptoms successfully'.format(
                request.session['phone_number'])
            )

        if user.verification_code:
            request.session['code'] = user.verification_code

            return redirect(results)
        else:
            """Send verification code to user phone number."""
            send_verification_code(request)

            return redirect(verify_user)

    return render(
        request,
        'info/symptoms.html',
        {
            'title': 'Symptoms',
            'form': symptoms_form
        }
    )


def verify_user(request):
    """Renders the verification page."""
    assert isinstance(request, HttpRequest)
    logger.info('Rendering verification page')

    code = request.session['code']
    error_message = ''
    verification_form = VerificationForm(request.POST or None)

    if verification_form.is_valid():
        logger.info('Verification form is valid')
        user_code = verification_form.cleaned_data.get('verification_code')

        if user_code == code:
            Users.objects.filter(
                phone_number=request.session['phone_number']
            ).update(verification_code=code)

            logger.info('{}: updated verification code successfully'.format(
                request.session['phone_number'])
            )

            return redirect(results)
        else:
            error_message = "The verification code you entered is incorrect!"

    return render(
        request,
        'info/verification.html',
        {
            'title': 'Verification',
            'message': error_message
        }
    )


def results(request):
    """Renders the results page."""
    assert isinstance(request, HttpRequest)
    logger.info('Rendering results page')

    if 'phone_number' in request.session and 'code' in request.session:
        logger.info('{}: executing results functions'.format(
            request.session['phone_number'])
        )
        user = Users.objects.get(phone_number=request.session['phone_number'])

        flu_like_cases = CoronaSymptoms.objects.filter(
            user_symptoms__overlap=[COUGHING_OR_SNEEZING, RUNNY_NOSE],
            user__county=user.county
        ).count()

        suspected_cases = CoronaSymptoms.objects.filter(
            user_symptoms__len__gte=4,
            user__county=user.county
        ).count()

        fever_or_breathing_difficulty = CoronaSymptoms.objects.filter(
            user_symptoms__overlap=[FEVER, BREATHING_DIFFICULTY],
            user__county=user.county
        ).count()

        flew_in_recently = CoronaSymptoms.objects.filter(
            user__arrived_recently=True,
            user__county=user.county
        ).count()

        first_corona_case = date(2020, 3, 13)
        date_today = date.today()
        days = (date_today - first_corona_case).days

        household = get_county_population(user.county)

        chance_of_contracting = round(
            ((suspected_cases/household) * 100), 4
        )

        e = 2.7182818
        k = 0.3465735
        a = 1  # initial case
        total_cases = math.ceil(a * (e ** (days * k)))

        logger.info('{}: saving results to dictionary'.format(
            request.session['phone_number'])
        )
        info = {
            'flu_like': flu_like_cases, 'suspected_cases': suspected_cases,
            'fever_or_breathing_difficulty': fever_or_breathing_difficulty,
            'flew_in_recently': flew_in_recently, 'chance_of_contracting': chance_of_contracting,
            'total_cases': total_cases, 'county': user.county
        }

    return render(
        request,
        'info/results.html',
        {
            'title': 'Results',
            'info': info
        }
    )
