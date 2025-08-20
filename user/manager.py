from django.contrib.auth.models import BaseUserManager

class CustomAccountManager(BaseUserManager):
    # Custom manager for the Account model
    # This manager provides methods to create user and superuser accounts.
    # It handles the creation of users with email and username fields.
    # It also ensures that the email is normalized and unique.
    # create_user Method: Creates a regular user with email and username.
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # create_superuser Method: Creates a superuser with all permissions.
    # It ensures that the superuser has is_staff and is_superuser set to True.
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get('is_verified') is not True:
            raise ValueError("Superuser must have is_verified=True.")

        return self.create_user(email, username, password, **extra_fields)