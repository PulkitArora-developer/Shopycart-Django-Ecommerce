from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self,first_name,last_name,email,username,password=None):
        if not email:
            raise ValueError("Email Address is Required")
        if not username:
            raise ValueError("Username is Required")

        user = self.model(
            email = self.normalize_email(email),  # normalise_email convert any upper letter to small letter
            username = username,
            first_name = first_name,
            last_name = last_name
        )

        user.set_password(password)
        user.save(using =  self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            first_name = first_name,
            last_name = last_name,
            email = self.normalize_email(email),
            username = username,
            password = password,

        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using = self._db)
        return user


class Account(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length = 50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    objects = MyAccountManager()

    def full_name(self):
        return self.first_name +" "+self.last_name
    def __str__(self):
        return self.email

    def has_perm(self, perm_list, obj=None):  # has permission
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE)
    address = models.CharField(max_length=250,blank=True)
    country = models.CharField(max_length=100,blank=True)
    state = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=15,blank=True)
    profile_picture = models.ImageField(blank=True,upload_to='userprofile')

    def __str__(self):
        return self.user.first_name

