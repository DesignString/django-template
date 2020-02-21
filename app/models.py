from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_extensions.db.fields import RandomCharField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SoftDeletionQuerySet(models.QuerySet):

    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def force_delete(self):
        return self.get_queryset().delete()


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def force_delete(self):
        super(SoftDeletionModel, self).delete()


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given username and password."""
        if not email:
            raise ValueError('The given email must be set')
        # username = self.normalize_email(username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given username and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given username and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, SoftDeletionModel):
    username = None
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='users', blank=True, null=True, max_length=500)
    is_superuser = models.BooleanField(default=0, verbose_name="Root User",
                                       help_text="User will have all permissions without explicitly assigning them.")
    is_staff = models.BooleanField(default=0, verbose_name="System Admin",
                                   help_text="User will have all permissions without explicitly assigning them.")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'ds_users'
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self._full_name()

    def _full_name(self):
        full_name = ""
        if self.first_name:
            full_name += self.first_name + " "
        if self.last_name:
            full_name += self.last_name + " "
        return full_name.strip()



