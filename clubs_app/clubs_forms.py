from django import forms
from clubs_app.models import Club, Award, Member, SocialMedia, Campus, Department, Tag, ClubUser, StaffCordinate
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import ClearableFileInput
from django.core.files.storage import default_storage
from datetime import datetime, date
from ckeditor.widgets import CKEditorWidget


current_date = date.today()

class SocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        fields = ['website', 'facebook', 'youtube', 'instagram', 'x']
        widgets = {
            'website': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Website',}),
            'facebook': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Facebook',}),
            'youtube': forms.TextInput(attrs={'type': 'text', 'placeholder': 'YouTube',}),
            'instagram': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Instagram',}),
            'x': forms.TextInput(attrs={'type': 'text', 'placeholder': 'X',}),
        }

class StaffCordinateForm(forms.ModelForm):
    staff_name = forms.CharField(
        label='staff_name',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Name',
        })
    )
    
    staff_designation = forms.CharField(
        label='staff_designation',
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Designation',
        })
    )

    
    staff_url = forms.CharField(
        label='staff_url',
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Staff URL',
        })
    )

    staff_pic_url = forms.CharField(
        label='staff_pic_url',
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Staff Profile Image URL',
        })
    )
    

    staff_phone = forms.IntegerField(label='contact', max_value=9999999999, widget=forms.NumberInput(attrs={'step': 1, 'placeholder': 'Please enter a 10-digit Phone Number'}),
        required=False)

    

    class Meta:
        model = StaffCordinate
        fields = ('staff_name', 'staff_url', 'staff_designation', 'staff_pic_url', 'staff_phone')
        # widget={
        # }

class MemberForm(forms.ModelForm):
    member_name = forms.CharField(
        label='Member Name',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Name',
        })
    )
    
    email = forms.CharField(
        label='email',
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Email',
        })
    )

    
    pesu_register_no = forms.CharField(
        label='pesu_register_no',
        required=False,
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Register No.',
        })
    )
    
    STUDENT_CO = (
        (True, 'Yes'),
        (False, 'No'),
    )
    student_co = forms.ChoiceField(
        choices=STUDENT_CO, label='student_co', required=True
    )

    member_contact = forms.IntegerField(label='contact', max_value=9999999999, widget=forms.NumberInput(attrs={'step': 1, 'placeholder': 'Please enter a 10-digit Phone Number'}),
        required=False)

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'nice-select chosen-select no-search-select'}),
        required=False
    )

    class Meta:
        model = Member
        fields = ('member_name', 'member_pic', 'pesu_register_no', 'student_co', 'email', 'member_contact', 'department')
        widget={
            'member_pic': forms.FileInput(attrs={'class': 'upload'}),
            'student_co': forms.RadioSelect(),
        }


class AwardForm(forms.ModelForm):
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'number',
            'min': 2000, 'max': (5+current_date.year),
            })
    )

    class Meta:
        model = Award
        fields = ('award_name', 'compitation_name', 'award_image', 'organizer', 'year', 'external_link')
        # exclude= ('club',)
        widgets = {
            'award_name': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Award Name', 'required': True,}),
            'award_image': forms.FileInput(attrs={'class': 'upload'}),
            'compitation_name': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Commpitation Name', 'required': True,}),
            'organizer': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Organizer',}),
            'external_link': forms.TextInput(attrs={'type': 'text', 'placeholder': 'External Link',}),
        }


from django.core.exceptions import ValidationError
from PIL import Image
import io
from django.core.files.base import ContentFile
from google.cloud import storage
from django.conf import settings
from datetime import datetime


class ClubCreationForm(forms.ModelForm):
    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Title',
            'required': True,
        })
    )

    email = forms.CharField(
        label='email',
        widget=forms.TextInput(attrs={
            'type': 'email',
            'placeholder': 'Club Email Id',
        }),
        required= False,
    )

    permalink = forms.CharField(
        label='Permalink',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Permalink',
            'required': True,
        })
    )
    
    background_color = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'color',
            'style':'width:100%;',
        })
    )
    
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Description',
        }),
        required= False,
    )

    

    RIBBON = (
        ('Popular', 'Popular'),
        ('Recomended', 'Recomended'),
        ('New', 'New'),
        ('Other', 'Other'),
    )
    ribbon = forms.ChoiceField(
        choices=RIBBON,
        label='Ribbon',
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'form-input-field django-radio'}),
    )

    staff_co = forms.CharField(
        widget=forms.Textarea(attrs={
            'cols': 40,
            'rows': 3,
            'placeholder': 'Type your text here..'
        }),
        initial='',
        required=False
    )

    student_co = forms.CharField(
        widget=forms.Textarea(attrs={
            'cols': 40,
            'rows': 3,
            'placeholder': 'Type your text here..'
        }),
        initial='',
        required=False
    )
    
    MAX_IMAGE_SIZE = 500 * 1024  # 500 KB

    club_image = forms.FileField(
        label='Upload Image',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'upload',
            'id': 'formFile',
            'accept': '.jpg,.jpeg,.png',
        })
    )
    
    def clean_club_image(self):
        club_image = self.cleaned_data.get('club_image')
        if club_image:
            # Validate file size
            if club_image.size > self.MAX_IMAGE_SIZE:
                raise ValidationError("File size cannot exceed 500KB.")
            
            image = Image.open(club_image)
            if image.format not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Upload an image with jpg or png format.')
        return club_image

    def save(self, commit=True):
        # Handle image renaming and replacement
        instance = super().save(commit=False)
        club_image = self.cleaned_data.get('club_image')
        old_club_image = instance.club_image if instance.pk else None  # Check if instance exists
        
        if club_image:
            # Rename and compress image
            filename = f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}_{club_image.name}'
            instance.club_image.name = filename
            
            image = Image.open(club_image)
            compressed_image_buffer = io.BytesIO()
            if image.format == 'jpeg':
                image.save(compressed_image_buffer, format='jpeg', quality=85)
            elif image.format == 'png':
                image.save(compressed_image_buffer, format='png', optimize=True)
            else:
                image.save(compressed_image_buffer, format=image.format, quality=85)
            
            compressed_image = ContentFile(compressed_image_buffer.getvalue(), filename)
            instance.club_image = compressed_image

            # Remove old image from the bucket
            if old_club_image and old_club_image.name != filename:
                try:
                    client = storage.Client()
                    bucket = client.bucket(settings.BUCKET_NAME)
                    blob = bucket.blob(old_club_image.name)
                    blob.delete()
                except Exception as e:
                    raise ValidationError('Error deleting old image from bucket.')

        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relationships
        return instance

    class Meta:
        model = Club
        fields = (
            'title', 'permalink', 'description', 'email', 'about', 'ribbon', 'founded_on',
            'background_color', 'club_image', 'campus', 'department', 'tag', 'staff_co'
        )
        widgets = {
            'founded_on': forms.TextInput(attrs={'type': 'date', 'required': False}),
            # 'club_image': forms.FileInput(attrs={'class': 'upload'}),
            
            # 'ribbon': forms.ChoiceField(attrs={'class': 'form-input-field django-chickbox'}),
            'campus': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
            'department': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
            'tag': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        }
        
class UserClubEditForm(forms.ModelForm):
    # email = forms.CharField(
    #     label='email',
    #     widget=forms.TextInput(attrs={
    #         'type': 'email',
    #         'placeholder': 'Club Email Id',
    #     }),
    #     required= False,
    # )
    # background_color = forms.CharField(
    #     widget=forms.TextInput(attrs={
    #         'type': 'color',
    #         'style':'width:100%;',
    #     })
    # )
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Description',
        }),
        required= False,
    )
    class Meta:
        model = Club
        fields = (
            'description', 'about','founded_on',
        )
        widgets = {
            'founded_on': forms.TextInput(attrs={'type': 'date', 'required': False}),
        }
        

class OLDClubCreationForm(forms.ModelForm):   

    title = forms.CharField(
        label='Title',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Title',
            'required': True,
        })
    )

    email = forms.CharField(
        label='email',
        widget=forms.TextInput(attrs={
            'type': 'email',
            'placeholder': 'Club Email Id',
        }),
        required= False,
    )

    permalink = forms.CharField(
        label='Permalink',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Permalink',
            'required': True,
        })
    )
    
    background_color = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'color',
            'style':'width:100%;',
        })
    )
    
    description = forms.CharField(
        label='Description',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Club Description',
        }),
        required= False,
    )

    

    RIBBON = (
        ('Popular', 'Popular'),
        ('Recomended', 'Recomended'),
        ('New', 'New'),
        ('Other', 'Other'),
    )
    ribbon = forms.ChoiceField(
        choices=RIBBON, label='ribbon', required=False
    )

    staff_co = forms.CharField(
        widget=forms.Textarea(attrs={
            'cols': 40,
            'rows': 3,
            'placeholder': 'Type your text here..'
        }),
        initial='',
        required=False
    )

    student_co = forms.CharField(
        widget=forms.Textarea(attrs={
            'cols': 40,
            'rows': 3,
            'placeholder': 'Type your text here..'
        }),
        initial='',
        required=False
    )

    # user = forms.ModelChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}), queryset=ClubUser.objects.all(), required=False)
    class Meta:
        model = Club
        fields = ('title', 'permalink', 'description', 'email', 'about', 'ribbon', 'founded_on', 'background_color', 'club_image', 'campus', 'department', 'tag', 'staff_co'
                #   , 'user'
                  )
        # about = forms.CharField(widget=CKEditorWidget())
        widgets = {
            'founded_on': forms.TextInput(attrs={'type': 'date', 'required': False}),
            'club_image': forms.FileInput(attrs={'class': 'upload'}),
            'campus': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
            'department': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
            'tag': forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        }

class ClubUserForm(UserCreationForm):

    username = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Example@pes.edu',
                # 'pattern': '.+@pes\.edu$',
                'title': 'Please enter a valid email address',
                'class': 'my-email-input-class',
                'required': True,
            }
        )
    ) 
    def clean_username(self):
        username = self.cleaned_data['username']
        cleaned_username = username.strip()  # Remove leading and trailing whitespace
        return cleaned_username
    

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class':'pass-input'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class':'pass-input'}), required=True)


    class Meta:
        model = ClubUser
        fields = ('username', 'password1', 'password2')
        exclude= ('is_superuser', 'is_staff', 'is_active')
        # widgets = {
        #     'pic': forms.FileInput(attrs={'class': 'upload'}),
        # }
        
    # def __init__(self, *args, **kwargs):
    #     super(ClubUserForm, self).__init__(*args, **kwargs)
    #     if self.instance and self.instance.pk:
    #         self.fields['password1'].widget = forms.HiddenInput()
    #         self.fields['password1'].required = False
    #         self.fields['password2'].widget = forms.HiddenInput()
    #         self.fields['password2'].required = False



class CampusForm(forms.ModelForm):
    campus = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Campus',
            'required': True,
        })
    )
    campus_navbar = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Display on Navbar',
            'required': True,
            'class': 'my-class',
        })
    )
    campus_priority = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Campus Priority',
            'required': True,
            'class': 'my-class',
        })
    )
    PIN_TO_NAVBAR = (
        (True, 'Yes'),
        (False, 'No'),
    )    
    navbar_display = forms.ChoiceField(
        choices=PIN_TO_NAVBAR, label='navbar_display', widget=forms.RadioSelect, required=True
    )
    campus_permalink = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Campus Permalink',
            'required': True,
            'class': 'my-class',
        })
    )
    class Meta:
        model = Campus
        fields =('campus', 'campus_navbar', 'campus_priority', 'campus_permalink',)


class DepartmentForm(forms.ModelForm):
    department = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Department',
            'required': True,
            'class': 'my-class',
        })
    )
    department_navbar = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Display on Navbar',
            'required': True,
            'class': 'my-class',
        })
    )
    department_priority = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Department Priority',
            'required': True,
            'class': 'my-class',
        })
    )
    PIN_TO_NAVBAR = (
        (True, 'Yes'),
        (False, 'No'),
    )    
    navbar_display = forms.ChoiceField(
        choices=PIN_TO_NAVBAR, label='navbar_display', widget=forms.RadioSelect, required=True
    )
    department_permalink = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Department Permalink',
            'required': True,
            'class': 'my-class',
        })
    )
    class Meta:
        model = Department
        fields ='__all__'


class TagForm(forms.ModelForm):
    tag = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Tag',
            'required': True,
            'class': 'my-class',
        })
    )
    tag_navbar = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Display on Navbar',
            'required': True,
            'class': 'my-class',
        })
    )
    tag_priority = forms.IntegerField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Tag Priority',
            'required': True,
            'class': 'my-class',
        })
    )
    PIN_TO_NAVBAR = (
        (True, 'Yes'),
        (False, 'No'),
    )    
    navbar_display = forms.ChoiceField(
        choices=PIN_TO_NAVBAR, label='navbar_display', widget=forms.RadioSelect, required=True
    )
    tag_permalink = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Tag Permalink',
            'required': True,
            'class': 'my-class',
        })
    )
    class Meta:
        model = Tag
        fields ='__all__'



class AdminUserCreationForm(UserCreationForm):

    # MAX_IMAGE_SIZE = 300 * 1024  # 300KB in bytes

    # def clean_pic(self):
    #     pic = self.cleaned_data.get('pic', None)
    #     if pic:
    #         if pic.size > self.MAX_IMAGE_SIZE:
    #             raise ValidationError("Image file size cannot exceed 300KB")
    #     return pic
        
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Alica',
            'required': True,
            'class': 'my-class',
        })
    )

    username = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Example@pes.edu',
                # 'pattern': '.+@pes\.edu$',
                'title': 'Please enter a valid email address',
                'class': 'my-email-input-class',
                'required': True,
            }
        )
    ) 
    def clean_username(self):
        username = self.cleaned_data['username']
        cleaned_username = username.strip()  # Remove leading and trailing whitespace
        return cleaned_username
    

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class':'pass-input'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class':'pass-input'}), required=True)

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        required=True,
    )

    class Meta:
        model = ClubUser
        fields = ('name', 'username', 'password1', 'password2', 'is_superuser', 'groups', 'is_staff', 'is_active')
        # widgets = {
        #     'pic': forms.FileInput(attrs={'class': 'upload'}),
        # }



class AdminUserChangeForm(forms.ModelForm):
    # MAX_IMAGE_SIZE = 300 * 1024  # 300KB in bytes

    # def clean_pic(self):
    #     pic = self.cleaned_data.get('pic', None)
    #     if pic:
    #         if pic.size > self.MAX_IMAGE_SIZE:
    #             raise ValidationError("Image file size cannot exceed 300KB")
    #     return pic


    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={
            'type': 'text',
            'placeholder': 'Alica',
            'required': True,
            'class': 'my-class',
        })
    )

    username = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Example@pes.edu',
                # 'pattern': '.+@pes\.edu$',
                'title': 'Please enter a valid PES email address',
                'class': 'my-email-input-class',
                'required': True,
            }
        )
    )
    def clean_username(self):
        username = self.cleaned_data['username']
        cleaned_username = username.strip()  # Remove leading and trailing whitespace
        return cleaned_username
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        required=True,
    )
    

    class Meta:
        model = ClubUser
        fields = ('name', 'username', 'is_superuser', 'groups', 'is_staff', 'is_active')
        # widgets = {
        #     'pic': ClearableFileInput(attrs={'class': 'upload'}),
        # }



class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(
        # content_type_id__in=[1, 4, 18, 19, 20]
    ),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']


class GroupPermissionForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(
        # content_type_id__in=[1, 4, 18, 19, 20]
    ),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-input-field django-chickbox'}),
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']