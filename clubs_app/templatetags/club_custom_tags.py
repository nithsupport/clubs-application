from django import template
from clubs_app.models import Club, ClubUser, Tag, Campus, Department
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

register = template.Library()

@register.filter
def is_user_in(users, user):
    return user in users


@register.filter
def popular_clubs(user):
    popular_clubs = Club.objects.filter(publish=True, ribbon__icontains='Popular').count()
    return popular_clubs

@register.filter
def recomended_clubs(user):
    recomended_clubs= Club.objects.filter(publish=True, ribbon__icontains='Recomended').count()
    return recomended_clubs

@register.filter
def new_clubs(user):
    new_clubs = Club.objects.filter(publish=True, ribbon__icontains='New').count()
    return new_clubs

@register.filter
def total_clubs(user):
    total_clubs = Club.objects.filter(publish=True).count()
    return total_clubs


@register.filter
def all_group(user):
    return user.groups.exists()


@register.filter
def club_user_check(user, club_id):
    if user.is_authenticated:
        return user.is_superuser or Club.objects.filter(pk=club_id, user__pk=user.pk).exists()
    else:
        return False







@register.filter
def check_requested_permissions(user, permission_codename):
    if user.is_authenticated:
        if user.is_superuser:
            return True
        try:
            return Permission.objects.get(codename=permission_codename, group__user=user)
        except Permission.DoesNotExist:
            return False
    else:
        return False
    


@register.filter
def list_of_image(list_of_image):
    return list_of_image[:5]

@register.filter
def archive_club(user):
    archive_club= Club.objects.filter(publish=False).count()
    return archive_club


@register.filter
def get_tags(tags):
    return Tag.objects.filter(navbar_display=True).order_by('tag_priority')
     

@register.filter
def get_campus(campus):
    return Campus.objects.filter(navbar_display=True).order_by('campus_priority')


@register.filter
def get_departments(departments):
    return Department.objects.filter(navbar_display=True).order_by('department_priority')

@register.filter
def remove_spaces(value):
    return value.replace(" ", "")

@register.filter
def add_hash_tags(value):
    return value.replace(",", ", #")



