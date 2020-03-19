from django.test import TestCase
from info.models import Users, CoronaSymptoms
from info.data_choices import (
    COUGHING_OR_SNEEZING, FATIGUE, FEVER,
    RUNNY_NOSE, BREATHING_DIFFICULTY, SORE_THROAT
)


class UsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Users.objects.create(
                phone_number="+254704845040",
                county='KAJIADO'
        )

    def test_phone_number_label(self):
        field_label = Users._meta.get_field('phone_number').verbose_name
        self.assertEquals(field_label, 'phone_number')

    def test_user_phone_number(self):
        user = Users.objects.first()
        self.assertEquals("+254704845040", user.phone_number.as_e164)

    def test_user_arrived_recently(self):
        user = Users.objects.first()
        self.assertEquals(False, user.arrived_recently)

    def test_user_is_not_verified(self):
        user = Users.objects.first()
        self.assertEquals(None, user.verification_code)


class CoronaSymptomsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Users.objects.create(
                phone_number="+254704845040",
                county='KAJIADO'
        )

    def test_user_can_create_symptoms(self):
        user = Users.objects.first()
        CoronaSymptoms.objects.create(
            user=user,
            user_symptoms=[
                COUGHING_OR_SNEEZING, FATIGUE, FEVER, RUNNY_NOSE,
                BREATHING_DIFFICULTY, SORE_THROAT]
        )
        user = CoronaSymptoms.objects.first()

        self.assertEquals(6, len(user.user_symptoms))

    def test_user_can_create_empty_symptoms(self):
        user = Users.objects.first()
        symptoms = []

        CoronaSymptoms.objects.create(
            user=user,
            user_symptoms=symptoms
        )
        user = CoronaSymptoms.objects.first()

        self.assertEquals(0, len(user.user_symptoms))
