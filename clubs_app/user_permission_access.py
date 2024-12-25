from django.db.models import Q
from django.contrib.auth.models import Permission
from .models import Club


# -----------------Admin dashboard permissions----------------------
# Checking all given permissions of admin dashboard

def check_requested_user_permissions(user, desired_permissions):
    if user.is_superuser:
        return True
    has_all_permissions = Permission.objects.filter(
        codename__in=desired_permissions,
        group__user=user
    ).all().values_list('codename', flat=True)

    return all(permission in has_all_permissions for permission in desired_permissions)



# -----------------End admin dashboard permissions----------------------

from functools import wraps
from django.http import HttpResponseRedirect

def user_passes_test_with_permalink(test_func, login_url=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            club_permalink = kwargs.get('club_permalink')
            if test_func(request.user, club_permalink):
                return view_func(request, *args, **kwargs)
            return HttpResponseRedirect(login_url)
        return _wrapped_view
    return decorator

# -------------Edit club user details permisssions-----------------
# Checking only club user
def check_only_club_user_permissions(requested_user, permalink=None, desired_permissions=None):
    if requested_user.is_superuser:
        return True
    if permalink:
        if requested_user.is_active and requested_user.is_staff:
            if requested_user.is_superuser or Club.objects.filter(permalink=permalink, users__pk=requested_user.pk).exists():
                return True
        if requested_user.is_authenticated:
            club_details = Club.objects.get(permalink=permalink, users__pk=requested_user.pk)
            if club_details:
                return True
    elif desired_permissions:
        has_all_permissions = Permission.objects.filter(
            codename__in=desired_permissions,
            group__user=requested_user
        ).all().values_list('codename', flat=True)

        return all(permission in has_all_permissions for permission in desired_permissions)
    else:
        return False

# Checking all given permissions of edit staff   
def check_given_permissions(requested_user, primary_key, check_permissions):
    if requested_user.is_active and requested_user.is_staff:
        
        if requested_user.is_superuser or requested_user.s_id==primary_key:
            return True
        else:
            has_all_permissions = Permission.objects.filter(
                codename__in=check_permissions,
                group__user=requested_user
            ).all().values_list('codename', flat=True)
            return all(permission in has_all_permissions for permission in check_permissions)
    else:
        return False



