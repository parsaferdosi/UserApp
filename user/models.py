from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from user.manager import CustomAccountManager
from django.utils.translation import gettext_lazy as _


class Account(AbstractBaseUser):
    #base authentication fields
    email = models.EmailField(_("email adress"),unique=True)
    username = models.CharField(max_length=30, unique=True)
    phone_number= models.CharField(max_length=15,unique=True,blank=True, null=True)
    #additional fields
    PFP= models.ImageField(upload_to='profile_pics/', default='default.jpg')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio=models.TextField(blank=True, null=True)
    #status fields
    is_active = models.BooleanField(default=True)
    # is_verified=models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    #timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    # Meta options
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = CustomAccountManager()

    def __str__(self):
        return self.email