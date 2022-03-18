from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models

# Create your models here.

fs = FileSystemStorage(location='/media/')

MALE = 'M'
FEMALE = 'F'
OTHERS = 'O'
GENDER_CHOICES = [
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (OTHERS, 'Others')
]


class UserProfile(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)], default=18)
    description = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/', storage=fs, default='images/obarock.png',
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])
    updated_at = models.DateTimeField(auto_now=True)


class UserLookingFor(models.Model):
    class Meta:
        abstract = True

    lfAgeFrom = models.IntegerField(null=True, blank=True)
    lfAgeTo = models.IntegerField(null=True, blank=True)
    lfGender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser, UserProfile, UserLookingFor):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Match(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
