from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

MALE = 'M'
FEMALE = 'F'
OTHERS = 'O'
GENDER_CHOICES = [
    (MALE, 'Male'),
    (FEMALE, 'Female'),
    (OTHERS, 'Others')
]
APPEARENCES = 'A'
FIRST_SIGHT_LOVE = 'F'
UNDECIDED = 'U'
ALCHEMY = 'L'
CRITERIA_CHOICES = [
    (APPEARENCES, 'Appearences'),
    (FIRST_SIGHT_LOVE, 'First Sight love'),
    (ALCHEMY, 'Alchemy'),
    (UNDECIDED, 'Undecided'),
]


def upload_to(instance, filename):
    return '{filename}'.format(filename=filename)


class UserProfile(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=100, default='')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)], default=18)
    description = models.CharField(max_length=255, default="")
    image = models.ImageField(default='./neutral.png', null=True, upload_to=upload_to,
                              validators=[
                                  FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg', 'webp', 'avif'])])
    updated_at = models.DateTimeField(auto_now=True)


class UserLookingFor(models.Model):
    class Meta:
        abstract = True

    lf_age_from = models.IntegerField(null=True, blank=True)
    lf_age_to = models.IntegerField(null=True, blank=True)
    lf_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE)
    lf_criteria = models.CharField(max_length=1, choices=CRITERIA_CHOICES, default=UNDECIDED)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser, UserProfile, UserLookingFor):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as inactive. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    content = models.CharField(max_length=255, default='test')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    match = models.ForeignKey('Match', on_delete=models.CASCADE, related_name='messages')


class Match(models.Model):
    class Meta:
        unique_together = ('user', 'match_user')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_user')
    created_at = models.DateTimeField(auto_now_add=True)


def expiration_date():
    return timezone.now() + timedelta(minutes=30)


class VerificationLink(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.CharField(max_length=128, primary_key=True)
    expire_at = models.DateTimeField(default=expiration_date())


class Like(models.Model):
    class Meta:
        unique_together = ('user', 'user_target')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_target')
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Like)
def if_both_like_generate_match(instance, created, **kwargs):
    if created:
        # check if a like exists with the same user and user_target
        if Like.objects.filter(user=instance.user_target, user_target=instance.user).exists() and Like.objects.filter(
                user=instance.user, user_target=instance.user_target).exists():
            # create a match
            Match.objects.get_or_create(user=instance.user, match_user=instance.user_target)


@receiver(post_save, sender=Match)
def if_match_deleted_delete_like(instance, created, **kwargs):
    if not created:
        # check if a like exists with the same user and user_target
        if Like.objects.filter(user=instance.user, user_target=instance.match_user).exists() or Like.objects.filter(
                user=instance.match_user, user_target=instance.user).exists():
            # delete the like
            Like.objects.get(user=instance.user, user_target=instance.match_user).delete()


@receiver(post_save, sender=User)
def if_user_banned_delete_all_matches(instance, created, **kwargs):
    if not created:
        if instance.is_banned:
            # delete all matches
            Match.objects.filter(user=instance).delete()
