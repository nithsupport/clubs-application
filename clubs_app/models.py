from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def create_user(self, username, password, **kwargs):
        user = self.model(username=username, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(username, password, **kwargs)

class ClubUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    username = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = ClubUser.objects.get(pk=self.pk)
            if original.password != self.password:
                self.password = make_password(self.password)
        else:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    

class ResetPassword(models.Model):
    reset_password_id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(ClubUser, on_delete=models.CASCADE)
    forget_password_token = models.CharField(max_length=255)
    forget_password_token_created_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


class Campus(models.Model):
    campus_id = models.AutoField(primary_key=True, unique=True)
    campus = models.CharField(max_length=255, unique=True)
    campus_navbar = models.CharField(max_length=255, unique=True)
    navbar_display = models.BooleanField(default=True)
    campus_priority = models.IntegerField(unique=True)
    campus_permalink = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.campus


class Department(models.Model):
    department_id = models.AutoField(primary_key=True, unique=True)
    department = models.CharField(max_length=255, unique=True)
    department_navbar = models.CharField(max_length=255, unique=True)
    navbar_display = models.BooleanField(default=True)
    department_priority = models.IntegerField(unique=True)
    department_permalink = models.CharField(max_length=255, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department
    

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True, unique=True)
    tag = models.CharField(max_length=100, unique=True)
    tag_navbar = models.CharField(max_length=255, unique=True)
    navbar_display = models.BooleanField(default=True)
    tag_priority = models.IntegerField(unique=True)
    tag_permalink = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag


# Create your models here.
class Club(models.Model):
    club_id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length = 255)
    permalink = models.CharField(max_length = 255, unique= True)
    description = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    ribbon = models.CharField(max_length=255, blank=True)
    email = models.EmailField(null=True, blank=True)
    founded_on = models.DateField()
    background_color = models.CharField(max_length = 255, default="#0095ff")
    likes = models.IntegerField(default=1)
    views = models.IntegerField(default=1)
    club_image = models.ImageField(upload_to='clubs/uploads/', blank=True)

    publish = models.BooleanField(default=True)

    campus = models.ManyToManyField(Campus, blank=True)
    department = models.ManyToManyField(Department, blank=True)
    tag = models.ManyToManyField(Tag, blank=True)

    users = models.ManyToManyField(ClubUser, blank=True, related_name='clubs')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.permalink


class StaffCordinate(models.Model):
    staff_cordinate_id= models.AutoField(primary_key=True, unique=True)
    staff_name = models.CharField(max_length=255)
    staff_pic_url= models.CharField(max_length=255, null=True, blank=True)
    staff_url= models.CharField(max_length=255, null=True, blank=True)
    staff_designation= models.CharField(max_length=255, null=True, blank=True)
    staff_phone= models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')], null=True, blank=True)
    club= models.ForeignKey(Club, on_delete=models.CASCADE) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.permalink



class SocialMedia(models.Model):
    social_media_id = models.AutoField(primary_key=True, unique=True)
    facebook = models.CharField(max_length=255, blank=True)
    youtube = models.CharField(max_length=255, blank=True)
    x = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.permalink


class Award(models.Model):
    award_id = models.AutoField(primary_key=True, unique=True)
    award_name = models.CharField(max_length=255)
    award_image= models.ImageField(upload_to='clubs/uploads/', blank=True)
    compitation_name = models.CharField(max_length=255, blank=True, null=True)
    organizer = models.CharField(max_length=255, blank=True, null=True)
    year = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{4}$')], blank=True, null=True)
    external_link = models.CharField(max_length=255, blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.permalink
    
    class Meta:
        ordering = ['-year', 'award_name']


class Member(models.Model):
    member_id = models.AutoField(primary_key=True, unique=True)
    member_name = models.CharField(max_length=255)
    pesu_register_no= models.CharField(max_length=255, blank=True, null=True)
    member_pic = models.ImageField(upload_to='clubs/uploads/', blank=True)
    student_co = models.BooleanField(default=False)
    email= models.CharField(max_length=255, blank=True, null=True)
    member_contact = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{10}$')], null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, blank=True, null=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.club.permalink
    
    class Meta:
        ordering = ['-student_co', 'member_name']