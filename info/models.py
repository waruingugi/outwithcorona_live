from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser
from outwithcorona.settings import ADMIN_PHONE_NO
from info.data_choices import COUNTY_CHOICES
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Users(AbstractBaseUser):
    time_stamp = models.DateTimeField(auto_now_add=True)
    phone_number = PhoneNumberField(
        "phone_number", blank=False, null=False, unique=True
    )
    county = models.CharField(
        max_length=50,
        choices=COUNTY_CHOICES,
        blank=False,
    )
    verification_code = models.IntegerField(null=True)
    arrived_recently = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['phone_number', 'county']
    USERNAME_FIELD = 'phone_number'

    class Meta:
        verbose_name = 'User'

    def __str__(self):
        return self.phone_number.as_e164

    @property
    def is_superuser(self):
        return (self.phone_number.as_e164 == ADMIN_PHONE_NO)

    @property
    def is_staff(self):
        return (self.phone_number.as_e164 == ADMIN_PHONE_NO)

    def has_perm(self, perm, obj=None):
        return (self.phone_number.as_e164 == ADMIN_PHONE_NO)

    def has_module_perms(self, app_label):
        return (self.phone_number.as_e164 == ADMIN_PHONE_NO)


class CoronaSymptoms(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    user_symptoms = ArrayField(
        models.CharField(max_length=200), blank=True
    )

    class Meta:
        verbose_name = 'Symptom'

    def __str__(self):
        return ("Phone number:{} \tSymptoms:{}".format(
            self.user.phone_number.as_e164, self.user_symptoms
            )
        )
