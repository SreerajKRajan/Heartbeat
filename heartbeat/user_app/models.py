from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, RegexValidator,MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class MyManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email       = self.normalize_email(email),
            username    = username,
        )

        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self,email,username,password):
        user = self.create_user(
            email       = self.normalize_email(email),
            username   = username,
            password    = password,
        )

        # user.is_admin       = True
        user.is_active      = True
        user.is_staff       = True
        user.is_superadmin  = True
        user.is_superuser   = True
        user.save(using=self._db)
        return user
    

class Account(AbstractBaseUser,PermissionsMixin):
    username      = models.CharField(max_length = 30)
    email         = models.EmailField(unique = True)
    # first_name    = models.CharField(max_length = 50)
    # last_name     = models.CharField(max_length = 50)
    is_active     = models.BooleanField(default = True)
    is_staff      = models.BooleanField(default = False)
    is_superadmin = models.BooleanField(default=False)
    is_blocked    = models.BooleanField(default=False)
    joined_on     = models.DateTimeField(auto_now_add = True)
    date_of_birth = models.DateField(blank = True, null = True, validators = [MaxValueValidator(limit_value=timezone.now().date())])
    phone         = models.BigIntegerField(unique = True, null = True, validators = [MinValueValidator(1000000000), MaxValueValidator(9999999999)])

    objects = MyManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    # def set_backend(self):
    #     self.backend = 'django.contrib.auth.backends.ModelBackend'
    #     self.save()

    def __str__(self):
        return self.email
    
    # def has_perm(self,perm,obj=None):
    #     return self.is_admin
    
    # def has_module_perms(self,add_label):
    #     return True
