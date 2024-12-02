from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings

from datetime import datetime
from datetime import timedelta

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    
    def create_user(self, phone, password, first_name, last_name, **extra_fields):
        if not phone:
            raise ValueError(_("The phone number must be set"))
        user = self.model(phone=phone, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        return self.create_user(phone, password, first_name, last_name, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return str(self.phone)