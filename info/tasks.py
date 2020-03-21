from __future__ import absolute_import, unicode_literals
import random
import africastalking
import outwithcorona.settings as settings
from retry import retry
import csv
from info.models import Users

# Initiate logging
import logging
import outwithcorona.outwithcorona_logger # noqa
# This retrieves a Python logging instance (or creates it)
logger = logging.getLogger(__name__)


def send_verification_code(request):
    """Four digit random code to verify user phone number."""
    logger.info('Executing send_verification code task')

    num = random.randrange(1, 10**4)
    code = str(num).zfill(4)
    request.session['code'] = str(code)

    message = 'Verification code is: ' + str(code)

    if 'phone_number' in request.session:
        phone_number = request.session['phone_number']

        """Send message to user."""
        send_sms(phone_number, message)


@retry((Exception), delay=10, backoff=3, max_delay=10)
def send_sms(recipient, message):
    if (
        all(
            [
                settings.AFRICASTALKING_API_KEY,
                settings.AFRICASTALKING_USERNAME
            ]
        )
    ):
        logger.info("Initializing send message settings.")
        try:
            africastalking.initialize(
                settings.AFRICASTALKING_USERNAME,
                settings.AFRICASTALKING_API_KEY
            )

            # Get the SMS service.
            sms = africastalking.SMS

            # The telephone numbers should be in international format.
            recipients = [recipient]

            response = sms.send(message, recipients)

            logger.info('Outgoing message sent to {}.\n Response: {}'.format(
                recipients, response
            ))
        except Exception as e:
            logger.error(
                '''
                An error ocurred while trying to send a message to {}.\n
                Error: {}
                '''.format(recipients, e)
            )
    else:
        logger.warning(
            '''Africastalking credentials are not set or phone number missing.
            Message aborted!
            '''
        )


def get_county_population(county):
    logger.info('{}: Executing get_county_population'.format(county))
    csv_file = csv.reader(open('data/County_Population_Density_2009.csv', "rt"), delimiter=",")

    for row in csv_file:
        if county == row[0]:
            house_hold_total = row[4]
            break

    return float(house_hold_total)


def number_of_users():
    number_of_users = Users.objects.all().count()
    logger.info('Return number of users less than one')
    return (number_of_users - 1)
