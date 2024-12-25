from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from clubs_app.image_compress_and_unique_filename import compress_img, create_unique_filename
from .user_permission_access import  (
    check_requested_user_permissions, user_passes_test_with_permalink, check_only_club_user_permissions
)

from clubs_app.models import Club, Award, Member, SocialMedia, Tag, Campus, Department, ClubUser, StaffCordinate
from clubs_app.clubs_forms import (
     CampusForm, DepartmentForm, TagForm, AdminUserCreationForm, AdminUserChangeForm,
     GroupForm, GroupPermissionForm,
     ClubCreationForm, UserClubEditForm, ClubUserForm, AwardForm, MemberForm, SocialMediaForm, StaffCordinateForm,
)
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
import os, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group, Permission
from PIL import Image
import io
from datetime import datetime, date
from google.cloud import storage
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.cache import cache


# Django Rest Framework
from django.http import JsonResponse
from .serializers import ClubSerializer

# Get the current date
current_date = date.today()


@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['add_socialmedia']), login_url='access-denied-page')
def add_social_media(request, club_permalink):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    if request.method == 'POST':
        form = SocialMediaForm(request.POST)
        if form.is_valid():
            if any([form.cleaned_data['website'], form.cleaned_data['facebook'], form.cleaned_data['youtube'], form.cleaned_data['instagram'], form.cleaned_data['x']]):
                social_media = form.save(commit=False)
                social_media.club_id = club_detail.club_id
                social_media.save()
            else:
                messages.error(request, 'Please provide data for at least one of the fields.')
        return redirect('add-social-media', club_permalink)  # Redirect to the same page after submission
    else:
        form =SocialMediaForm()

    context = {
        'club_detail':club_detail,
        'form': form,
    }
    return render(request, 'create_or_edit/create-edit-social-media.html', context)


@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['change_socialmedia']), login_url='access-denied-page')
def edit_social_media(request, club_permalink, social_media_id):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    social_media = get_object_or_404(SocialMedia, pk=social_media_id)
    if request.method == 'POST':
        form = SocialMediaForm(request.POST, instance=social_media)
        if form.is_valid():
            if any([form.cleaned_data['website'], form.cleaned_data['facebook'], form.cleaned_data['youtube'], form.cleaned_data['instagram'], form.cleaned_data['x']]):
                form.save()
            else:
                messages.error(request, 'Please provide data for at least one of the fields.')
        return redirect('add-social-media', club_permalink)  # Redirect to the same page after submission
    else:
        form =SocialMediaForm(instance=social_media)

    context = {
        'club_detail':club_detail,
        'form': form,
    }
    return render(request, 'create_or_edit/create-edit-social-media.html', context)


@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['delete_socialmedia']), login_url='access-denied-page')
def delete_single_social_media(request, club_permalink, social_media_id):
    delete_social_media= get_object_or_404(SocialMedia, pk=social_media_id)
    delete_social_media.delete()
    return redirect('add-social-media', club_permalink)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['add_award']), login_url='access-denied-page')
def create_award(request, club_permalink):
    initial_data= {'year':current_date.year}
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    if request.method == 'POST':
        award_form = AwardForm(request.POST)
        if award_form.is_valid():
            # Associate the club with the award before saving
            award = award_form.save(commit=False)
            award.club = club_detail
            award.save()
            return redirect('create-award', club_permalink)
    else:
        award_form= AwardForm(initial=initial_data)

    context={
        'club_detail':club_detail,
        'award_form':award_form,
    }
    return render(request, 'create_or_edit/create-edit-awards.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['change_award']), login_url='access-denied-page')
def edit_award(request, club_permalink, award_id):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    award_detail= get_object_or_404(Award, pk=award_id)
    if request.method == 'POST':
        award_form = AwardForm(request.POST, instance=award_detail)
        if award_form.is_valid():
            # Associate the club with the award before saving
            award_form.save()
            return redirect('create-award', club_permalink)
    else:
        award_form= AwardForm(instance=award_detail)

    context={
        'club_detail':club_detail,
        'award_detail':award_detail,
        'award_form':award_form,
    }
    return render(request, 'create_or_edit/create-edit-awards.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['add_staffcordinate']), login_url='access-denied-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_award']), login_url='access-denied-page')
def delete_award(request, club_permalink, award_id):
    award_detail= get_object_or_404(Award, pk=award_id)
    award_detail.delete()
    return redirect('create-award', club_permalink)


@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['add_member']), login_url='access-denied-page')
def create_member(request, club_permalink):
    initial_data= {'student_co':False}
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        if member_form.is_valid():
            # Associate the club with the member before saving
            member = member_form.save(commit=False)
            member.club = club_detail
            member.save()
            return redirect('create-member', club_permalink)
    else:
        member_form= MemberForm(initial=initial_data)

    context={
        'club_detail':club_detail,
        'member_form':member_form,
    }
    return render(request, 'create_or_edit/create-edit-members.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['change_member']), login_url='access-denied-page')
def edit_member(request, club_permalink, member_id):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    member_detail= get_object_or_404(Member, pk=member_id)
    if request.method == 'POST':
        member_form = MemberForm(request.POST, instance=member_detail)
        if member_form.is_valid():
            # Associate the club with the member before saving
            member_form.save()
            return redirect('create-member', club_permalink)
    else:
        member_form= MemberForm(instance=member_detail)

    context={
        'club_detail':club_detail,
        'member_detail':member_detail,
        'member_form':member_form,
    }
    return render(request, 'create_or_edit/create-edit-members.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['delete_member']), login_url='access-denied-page')
def delete_member(request, club_permalink, member_id):
    member_detail= get_object_or_404(Member, pk=member_id)
    member_detail.delete()
    return redirect('create-member', club_permalink)


@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['add_staffcordinate']), login_url='access-denied-page')
def create_staff_co(request, club_permalink):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    if request.method == 'POST':
        staff_co_form = StaffCordinateForm(request.POST)
        if staff_co_form.is_valid():
            # Associate the club with the staff_co before saving
            staff_co = staff_co_form.save(commit=False)
            staff_co.club = club_detail
            staff_co.save()
            return redirect('create-staff-cordinate', club_permalink)
    else:
        staff_co_form= StaffCordinateForm()

    context={
        'club_detail':club_detail,
        'staff_co_form':staff_co_form,
    }
    return render(request, 'create_or_edit/create-edit-staff-co.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['change_staffcordinate']), login_url='access-denied-page')
def edit_staff_co(request, club_permalink, staff_cordinate_id):
    club_detail= get_object_or_404(Club, permalink=club_permalink)
    staff_co_detail= get_object_or_404(StaffCordinate, pk=staff_cordinate_id)
    if request.method == 'POST':
        staff_co_form = StaffCordinateForm(request.POST, instance=staff_co_detail)
        if staff_co_form.is_valid():
            # Associate the club with the staff_co before saving
            staff_co_form.save()
            return redirect('create-staff-cordinate', club_permalink)
    else:
        staff_co_form= StaffCordinateForm(instance=staff_co_detail)

    context={
        'club_detail':club_detail,
        'staff_co_detail':staff_co_detail,
        'staff_co_form':staff_co_form,
    }
    return render(request, 'create_or_edit/create-edit-staff-co.html', context)

@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['delete_staffcordinate']), login_url='access-denied-page')
def delete_staff_co(request, club_permalink, staff_cordinate_id):
    staff_co_detail= get_object_or_404(StaffCordinate, pk=staff_cordinate_id)
    staff_co_detail.delete()
    return redirect('create-staff-cordinate', club_permalink)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['add_club']), login_url='access-denied-page')
def create_account(request):
    initial_data = {
        'ribbon': 'Other',
        'founded_on': current_date,
        'background_color': '#313c71',
    }

    if request.method == 'POST':
        club_form = ClubCreationForm(request.POST, request.FILES)
        user_form = ClubUserForm(request.POST)
        if club_form.is_valid() and user_form.is_valid():
            club = club_form.save()
            user = user_form.save()
            club.users.add(user)
            # messages.success(request, mark_safe(
            #     f'Just added a new user to the club. <a href="{reverse("club-details", kwargs={"club_permalink": club.permalink})}">View added Club</a>'
            # ))
            return redirect('club-details', club.permalink)
        else:
            messages.error(request, 'Error creating account.')
    else:
        club_form = ClubCreationForm(initial=initial_data)
        user_form = ClubUserForm()

    context = {
        'form': club_form,
        'user_form': user_form,
    }
    return render(request, 'create_or_edit/creating-account.html', context)

# def create_account(request):
#     initial_data= {'ribbon':'Other', 'founded_on':current_date, 'background_color':'#313c71'}

#     if request.method == 'POST':
#         club_form = ClubCreationForm(request.POST, request.FILES)
#         user_form = ClubUserForm(request.POST)
#         if club_form.is_valid() and user_form.is_valid():
#             club = club_form.save(commit=False)
#             club_image = club_form.cleaned_data.get('club_image')
#             if club_image:
#                 filename = create_unique_filename(club_image)
#                 club.club_image.save(filename)
#             club.save()
#             user = user_form.save(commit=False)
#             user.save()
#             club.users.add(user)
#             # Update related fields
#             tag = club_form.cleaned_data['tag']
#             campus = club_form.cleaned_data['campus']
#             department = club_form.cleaned_data['department']
            
#             club.tag.set(tag)  # Update tags
#             club.campus.set(campus)  # Update campus
#             club.department.set(department)  # Update department
#             messages.success(request, mark_safe(f'Just added a new user to the club. <a href="{redirect("club-details", club_permalink=club.permalink).url}">View added Club</a>'))
#             return redirect('create-account')
#         else:
#             messages.success(request, ('error'))
#     else:
#         club_form = ClubCreationForm(initial=initial_data)
#         user_form = ClubUserForm()
        
        
        
    #     form = ClubCreationForm(request.POST, request.FILES)
    #     user_form = ClubUserForm(request.POST)
        
    #     if form.is_valid():
    #         club = form.save(commit=False)  # Save the form data without committing it to the database
    #         # club_user= user_form.save(commit=False)
    #         # club_user.name= club.title
    #         # club_user.is_club= True
    #         # club_user.is_active= True
    #         # # club.email= club_user.username
    #         # club.user=club_user

    #         club_image = form.cleaned_data.get('club_image')
    #         if club_image:
    #             image = Image.open(club_image)
    #             compressed_image = compress_img(club_image)
                
    #             compressed_image_buffer = io.BytesIO()
    #             if image.format == 'JPEG':
    #                 compressed_image.save(compressed_image_buffer, format='JPEG')
    #             elif image.format == 'PNG':
    #                 compressed_image.save(compressed_image_buffer, format='PNG')
    #             else:
    #                 messages.error(request, 'Upload image with jpg format.')
    #                 return redirect('creating-account')  # Redirect to an error page
                    
    #             filename = create_unique_filename(club_image)
    #             club.club_image.save(filename, content=compressed_image_buffer)

    #         # club_user.save()
    #         club.save()
    #         # Update related fields
    #         tag = form.cleaned_data['tag']
    #         campus = form.cleaned_data['campus']
    #         department = form.cleaned_data['department']
            
    #         club.tag.set(tag)  # Update tags
    #         club.campus.set(campus)  # Update campus
    #         club.department.set(department)  # Update department

   
    #         messages.success(request, ('Just added a new user to the club and they should now be able to log in and start using the application.'))
    #         return redirect('club-details', club.permalink)
    # else:
    #     form = ClubCreationForm(initial=initial_data)
        # user_form= ClubUserForm()
    # context={
        
    #     'form': club_form,
    #     'user_form': user_form,
    # }
    # return render(request, 'create_or_edit/creating-account.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_club']), login_url='access-denied-page')
def edit_club_account(request, club_permalink):
    edit_club = get_object_or_404(Club, permalink=club_permalink)
    if request.method == 'POST':
        club_form = ClubCreationForm(request.POST, request.FILES, instance=edit_club)
        if club_form.is_valid():
            club = club_form.save()
            messages.success(request, mark_safe(
                f'Successfuly edited club <a href="{reverse("club-details", kwargs={"club_permalink": club.permalink})}">View Club</a>'
            ))
            # return redirect('club-details', club.permalink)
        else:
            messages.error(request, 'Error saving account.')
    else:
        club_form = ClubCreationForm(instance=edit_club)

    context = {
        'form': club_form,
        'club_detail': edit_club,
    }
    return render(request, 'create_or_edit/creating-account.html', context)



@login_required(login_url='login-page')
@user_passes_test_with_permalink(lambda user, club_permalink: check_only_club_user_permissions(user, club_permalink, ['change_club']), login_url='access-denied-page')
def user_edit_club_account(request, club_permalink):
    edit_club = get_object_or_404(Club, permalink=club_permalink)
    
    if request.method == 'POST':
        edit_club.description = request.POST.get('description')
        edit_club.about = request.POST.get('about')
        edit_club.save()
        return redirect('club-details', edit_club.permalink)
    
    context = {
        'form': edit_club,
        'club_detail': edit_club,
    }
    return render(request, 'create_or_edit/creating-account.html', context)



# @login_required(login_url='login-page')
# @user_passes_test(lambda user: check_only_club_user_permissions(user, club_permalink), login_url='access-denied-page')
# def user_edit_club_account(request, club_permalink):
#     edit_club = get_object_or_404(Club, permalink=club_permalink)
#     if request.method == 'POST':
#         edit_club.description= request.POST.get('description')
#         edit_club.about= request.POST.get('about')
#         edit_club.save()
#         return redirect('club-details', edit_club.permalink)
#     context = {
#         'form': edit_club,
#         'club_detail': edit_club,
#     }
#     return render(request, 'create_or_edit/creating-account.html', context)

@login_required(login_url='login-page')
def OLD_edit_club_account(request, club_permalink):
    @user_passes_test(lambda user: check_requested_user_permissions(user, ['change_club']), login_url='access-denied-page')
    def inner_edit_club_account(request, club_permalink):

        edit_club= get_object_or_404(Club, permalink=club_permalink)
        edit_club_user = edit_club.users.first()  # Assuming one user per club for simplicity
        if request.method == "POST":
            form = ClubCreationForm(request.POST, request.FILES, instance=edit_club)
            user_form = ClubUserForm(request.POST, instance=edit_club_user)
            if form.is_valid():
                club = form.save(commit=False)
                club_image = club.club_image
                old_club_image_path = edit_club.club_image

                if club_image and old_club_image_path != club_image:  # Compare paths
                    # Delete the old image from the Google Cloud Storage bucket
                    if old_club_image_path:
                        client = storage.Client()
                        bucket_name = settings.BUCKET_NAME  # Replace with your actual bucket name
                        blob_name = client.bucket(bucket_name)  # Replace with the path of the old image in the bucket
                        
                        try:
                            bucket = client.bucket(bucket_name)
                            blob = bucket.blob(blob_name)
                            blob.delete()
                        except Exception as e:
                            # Handle any exceptions that might occur during deletion
                            messages.error(request, 'Error deleting old image from bucket.')

                    image = Image.open(club_image)
                    compressed_image = compress_img(club_image)

                    compressed_image_buffer = io.BytesIO()
                    if image.format == 'JPEG':
                        compressed_image.save(compressed_image_buffer, format='JPEG')
                    elif image.format == 'PNG':
                        compressed_image.save(compressed_image_buffer, format='PNG')
                    else:
                        messages.error(request, 'Upload image with jpg format.')
                        return redirect('club-details', club.permalink)

                    filename = create_unique_filename(club_image)
                    club.club_image.save(filename, content=compressed_image_buffer)

        # if request.method == 'POST':
        #     form = ClubCreationForm(request.POST, request.FILES, instance=edit_club)
            
        #     if form.is_valid():
        #         club = form.save(commit=False)  # Save the form data without committing it to the database
                
        #         profile_club_image = form.cleaned_data.get('club_image') 
        #         old_profile_club_image_path = club.club_image.name

        #         if profile_club_image and old_profile_club_image_path != profile_club_image:  # Compare paths
        #             # Delete the old image from the Google Cloud Storage bucket
        #             if old_profile_club_image_path:
        #                 client = storage.Client()
        #                 bucket_name = settings.BUCKET_NAME  # Replace with your actual bucket name
        #                 blob_name = client.bucket(bucket_name)  # Replace with the path of the old image in the bucket
                        
        #                 try:
        #                     bucket = client.bucket(bucket_name)
        #                     blob = bucket.blob(blob_name)
        #                     blob.delete()
        #                 except Exception as e:
        #                     print(e)

        #             image = Image.open(profile_club_image)
        #             compressed_image = compress_img(image)

        #             compressed_image_buffer = io.BytesIO()
        #             if image.format == 'JPEG':
        #                 compressed_image.save(compressed_image_buffer, format='JPEG', quality=85, save=False)
        #             elif image.format == 'PNG':
        #                 compressed_image.save(compressed_image_buffer, format='PNG', save=False)
        #             else:
        #                 messages.error(request, 'Upload image with jpg format.')
        #                 return redirect('edit-club-account', club.permalink)

        #             filename = create_unique_filename(profile_club_image)
        #             club.club_image.save(filename, content=compressed_image_buffer, save=False)

                # Update related fields
                tag = form.cleaned_data['tag']
                campus = form.cleaned_data['campus']
                department = form.cleaned_data['department']
                
                club.tag.set(tag)  # Update tags
                club.campus.set(campus)  # Update campus
                club.department.set(department)  # Update department

                club.save()  # Save the club object with the cleaned username
                

    
                messages.success(request, ('Just added a new user to the club and they should now be able to log in and start using the application.'))
                return redirect('club-details', club.permalink)
        else:
            form = ClubCreationForm(instance=edit_club)
            user_form= ClubUserForm(instance=edit_club_user)
        context={
            
            'form': form,
            'user_form': user_form,
            'club_detail': edit_club,
        }
        return render(request, 'create_or_edit/creating-account.html', context)
    return inner_edit_club_account(request, club_permalink)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_club',]), login_url='access-denied-page')
def delete_club_from_db(request, club_id):
    delete_club= get_object_or_404(Club, pk= club_id)
    delete_club.delete()
    return redirect('archive-page')



@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['view_permission']), login_url='access-denied-page')
def group_create(request):
    form = GroupForm()
    all_user_groups = Group.objects.all()
    if check_requested_user_permissions(request.user, ['add_permission']):
        if request.method == 'POST':
            form = GroupForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('create_user_groups')
            
    context = {
        'form': form,
        'all_user_groups':all_user_groups
    }
    return render(request, 'admin/group_create.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_permission']), login_url='access-denied-page')
def group_permissions(request, group_id):
    
    all_user_groups = Group.objects.all()

    group = Group.objects.get(id=group_id)
    if request.method == 'POST':
        form = GroupPermissionForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('create_user_groups')
    else:
        form = GroupPermissionForm(instance=group)
    context = {
        'form': form,
        'group': group,
        'all_user_groups':all_user_groups
    }
    return render(request, 'admin/group_create.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_club',]), login_url='access-denied-page')
def archive_page(request):
    a = request.GET.get('archive-search') if request.GET.get('archive-search') != None else ''
    
    all_archive= Club.objects.filter(Q(title__icontains= a), publish=False).order_by('-updated_at')
    page_number = request.GET.get('page')
    clubs_par_page= 20
    all_archive= all_paginator(all_archive, page_number, clubs_par_page)
    context={
        
        'all_pages':all_archive,
    }
    return render(request, 'admin/archive-page.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['view_group']), login_url='access-denied-page')
def create_admin_user(request):
    form = AdminUserCreationForm()
    if request.user.is_superuser:
        club_groups = ClubUser.groups.through.objects.select_related('clubuser', 'group')
    else:
        club_groups = ClubUser.groups.through.objects.select_related('clubuser', 'group').filter(clubuser__is_superuser=False)
        
    if check_requested_user_permissions(request.user, ['add_group']):
        if request.method == 'POST':
            form = AdminUserCreationForm(request.POST, request.FILES)
            if form.is_valid():
                # admin_user = form.save(commit=False)
                admin_user = form.save()
                groups = form.cleaned_data['groups']
                admin_user.groups.set(groups)
                
                messages.success(request, 'User created successfully.')
                return redirect('create-admin-user')  # Replace 'club-list' with the URL name of the club list view
     
    context={
        'form': form,
        'club_groups': club_groups,
    }
    
    return render(request, 'admin/create_admin_user.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_group']), login_url='access-denied-page')
def edit_admin_user(request, admin_user_id):
    if request.user.is_superuser:
        club_groups = ClubUser.groups.through.objects.select_related('clubuser', 'group')
    else:
        club_groups = ClubUser.groups.through.objects.select_related('clubuser', 'group').filter(clubuser__is_superuser=False)

    admin_user = ClubUser.objects.get(pk=admin_user_id) 
    if request.method == 'POST':
        form = AdminUserChangeForm(request.POST, request.FILES, instance=admin_user)
        if form.is_valid():
            form.save()
            groups = form.cleaned_data['groups']
            admin_user.groups.set(groups)
            messages.success(request, 'club updated successfully.')
            return redirect('create-admin-user')  
    else:
        form = AdminUserChangeForm(instance=admin_user)

    context={
        'form': form,
        'club_groups':club_groups,
    }
    return render(request, 'admin/create_admin_user.html', context)



@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_group',]), login_url='access-denied-page')
def delete_user_from_db(request, user_id):
    delete_user= get_object_or_404(ClubUser, pk= user_id)
    delete_user.delete()
    return redirect('create-admin-user')



@login_required(login_url='login-page')
def dashboard(request):
    club_user= get_object_or_404(ClubUser, username=request.user.username)
    context = {
        'club_user':club_user,
    }
    return render(request, 'base/dashboard.html', context)


def club_views_counts(club_details):
    club_details.views = club_details.views + 1
    club_details.save()
    return club_details

@csrf_exempt
def like_club(request):
    if request.method == 'POST':
        pk = request.POST.get('pk', None)
        value = request.POST.get('key', None)
        print('club pk: ', pk)
        print('club likes: ', value)
        club = Club.objects.get(pk=pk)
        if club.likes is None or club.likes < 1:
            club.likes = 1

        if value == "like":
            club.likes += 1
        else:
            club.likes -= 1
        club.save()
        
        ctx = {'num_likes_count': club.likes}
        return HttpResponse(json.dumps(ctx), content_type='application/json')

# def club_details(request, club_permalink):
#     try:
#         if request.user.is_superuser or request.user.groups.exists():
#             club_details = get_object_or_404(Club, permalink=club_permalink)
#         else:
#             club_details = get_object_or_404(Club, permalink=club_permalink, publish=True)
#     except Club.DoesNotExist:
#         return render(request, 'handler/404.html')
    
#     club_details_serializer = ClubSerializer(club_details)
#     return JsonResponse(club_details_serializer.data, safe=False)


def club_details(request, club_permalink):
    club_details = cache.get(club_permalink)
    message = ""

    if club_details:
        message = "Data From Cache"
    else:
        try:
            if request.user.is_superuser or request.user.groups.exists():
                club_details = get_object_or_404(Club, permalink=club_permalink)
                cache.set(club_permalink, club_details, 300)  # Cache for 5 minutes
                message = "Data From DB (Admin or Group)"
            else:
                club_details = get_object_or_404(Club, permalink=club_permalink, publish=True)
                cache.set(club_permalink, club_details, 300)  # Cache for 5 minutes
                message = "Data From DB (Published)"
        except Club.DoesNotExist:
            return render(request, 'handler/404.html')
    
    similar_clubs = Club.objects.filter(publish=True).order_by('-club_id')[:5]
    
    club = club_views_counts(club_details)  # Assuming this is a valid function
    club_details = club

    try:
        previous_club = Club.objects.filter(club_id__lt=club_details.club_id, publish=True).last()
    except Club.DoesNotExist:
        previous_club = None

    try:
        next_club = Club.objects.filter(club_id__gt=club_details.club_id, publish=True).first()
    except Club.DoesNotExist:
        next_club = None

    if request.method == 'POST':
        return like_club(request)  # Call the like_club function for like/dislike actions

    context = {
        'club_details': club_details,
        'previous_club': previous_club,
        'next_club': next_club,
        'similar_clubs': similar_clubs,
        'message': message,  # Pass the message to the template
    }

    return render(request, 'base/club-details.html', context)

def member_list(request, club_permalink):
    club_details = get_object_or_404(Club, permalink= club_permalink)
    context={
        'club_details':club_details,
    }
    return render(request, 'base/member-list.html', context)

def award_list(request, club_permalink):
    club_details = get_object_or_404(Club, permalink= club_permalink)
    context={
        'club_details':club_details,
    }
    return render(request, 'base/award-list.html', context)


def all_clubs(request):
    q = request.GET.get('search') if request.GET.get('search') != None else ''
    clubs = Club.objects.filter(Q(title__icontains= q) | Q(permalink__icontains= q) | Q(email__icontains= q) | Q(users__username__icontains= q), publish=True).order_by('title', 'permalink')
    
    page_number = request.GET.get('page')
    clubs_par_page= 16
    clubs= all_paginator(clubs, page_number, clubs_par_page)
    context={
        'clubs':clubs,
    }
    return render(request, 'base/all-clubs.html', context)




# def index(request):
#     popular_clubs= Club.objects.filter(publish=True, ribbon__icontains='popular').order_by('-created_at')[:8]
#     popular_clubs_serializer = ClubSerializer(popular_clubs, many=True)
#     return JsonResponse(popular_clubs_serializer.data, safe=False)
# Create your views here.
def index(request):
    
    popular_clubs= Club.objects.filter(publish=True, ribbon__icontains='popular').order_by('-created_at')[:8]
    recomended_clubs= Club.objects.filter(publish=True, ribbon__icontains='recomended').order_by('-created_at')[:8]
    new_clubs= Club.objects.filter(publish=True, ribbon__icontains='new').order_by('-created_at')[:8]

    context={
        'popular_clubs':popular_clubs,
        'recomended_clubs':recomended_clubs,  
        'new_clubs':new_clubs,

    }
    return render(request, 'base/index.html', context)





#brows by campus, department, tag's, ribbons
def brows_campus(request, campus_permalink):
    title_icon = 'fas fa-university'
    campus = get_object_or_404(Campus, campus_permalink=campus_permalink)
    titles_name = campus.campus
    clubs = Club.objects.filter(campus__campus_permalink__icontains=campus_permalink, publish=True)
    total_clubs = clubs.count()
    page_number = request.GET.get('page')
    clubs_par_page = 16
    # Paginate the categorized clubs
    all_pages = all_paginator(clubs, page_number, clubs_par_page)
    context = {
        'titles_name': titles_name,
        'total_clubs': total_clubs,
        'all_pages': all_pages,
        'title_icon': title_icon,
    }
    return render(request, 'base/browse-by-page.html', context)

def browse_department(request, department_permalink):
    title_icon = 'fas fa-school'
    department= get_object_or_404(Department, department_permalink=department_permalink)
    titles_name = department.department
    clubs = Club.objects.filter(department__department_permalink__icontains=department_permalink, publish=True)
    total_clubs = clubs.count()
    page_number = request.GET.get('page')
    clubs_par_page= 16
    all_pages = all_paginator(clubs, page_number, clubs_par_page)
    context ={
        'titles_name':titles_name,
        'total_clubs': total_clubs,
        'all_pages': all_pages,
        'title_icon':title_icon,
        }
    return render(request, 'base/browse-by-page.html', context)

def brwose_tag(request, tag_permalink):
    title_icon = 'fas fa-tags'
    tag_name = get_object_or_404(Tag, tag_permalink=tag_permalink)
    titles_name = tag_name.tag
    clubs = Club.objects.filter(tag__tag_permalink__icontains=tag_permalink, publish=True)
    total_clubs = clubs.count()
    page_number = request.GET.get('page')
    clubs_par_page= 16
    all_pages = all_paginator(clubs, page_number, clubs_par_page)
    context ={
        'titles_name':titles_name,
        'total_clubs': total_clubs,
        'all_pages': all_pages,
        'title_icon':title_icon,
        }
    return render(request, 'base/browse-by-page.html', context)

def brwose_ribbon(request, ribbon):
    title_icon = 'fas fa-star'
    titles_name = ribbon
    clubs = Club.objects.filter(ribbon__icontains=ribbon, publish=True).order_by('title', 'permalink')
    total_clubs = clubs.count()
    page_number = request.GET.get('page')
    clubs_par_page= 16
    all_pages = all_paginator(clubs, page_number, clubs_par_page)
    context ={
        'titles_name':titles_name,
        'total_clubs': total_clubs,
        'all_pages': all_pages,
        'title_icon':title_icon,
        }
    return render(request, 'base/browse-by-page.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['add_campus']), login_url='access-denied-page')
def campus_settings(request):
    all_campus= Campus.objects.all().order_by('campus_priority')
    
    if request.method == 'POST':
        add_campus= CampusForm(request.POST)
        if add_campus.is_valid():
            add_campus.save()
            return redirect('campus-settings')
    else:
        initial_data = {'navbar_display': True}
        add_campus= CampusForm(initial=initial_data)
    context={
        'add_campus':add_campus,
        'all_campus':all_campus, 
        }
    return render(request, 'settings/add-edit-campus.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_campus']), login_url='access-denied-page')
def edit_single_campus(request, campus_id):
    campus = get_object_or_404(Campus, pk = campus_id)
    all_campus= Campus.objects.all().order_by('campus_priority')
    
    if request.method == 'POST':
        edit_campus= CampusForm(request.POST, instance=campus)
        if edit_campus.is_valid():
            edit_campus.save()
            return redirect('campus-settings')
    else:
        edit_campus= CampusForm(instance=campus)
    context={
        'edit_campus':edit_campus,
        'all_campus':all_campus, 
        }
    return render(request, 'settings/add-edit-campus.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_campus']), login_url='access-denied-page')
def delete_single_campus(request, campus_id):
    delete_campus= get_object_or_404(Campus, pk=campus_id)
    delete_campus.delete()
    return redirect('campus-settings')


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['add_department']), login_url='access-denied-page')
def department_settings(request):
    all_department= Department.objects.all().order_by('department_priority')
    
    if request.method == 'POST':
        add_department= DepartmentForm(request.POST)
        if add_department.is_valid():
            add_department.save()
            return redirect('department-settings')
    else:
        initial_data = {'navbar_display': True}
        add_department= DepartmentForm(initial=initial_data)

    context={
        'add_department':add_department,
        'all_department':all_department, 
        }
    return render(request, 'settings/add-edit-department.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_department']), login_url='access-denied-page')
def edit_single_department(request, department_id):
    department = get_object_or_404(Department, pk = department_id)
    all_department= Department.objects.all().order_by('department_priority')
    
    if request.method == 'POST':
        edit_department= DepartmentForm(request.POST, instance=department)
        if edit_department.is_valid():
            edit_department.save()
            return redirect('department-settings')
    else:
        edit_department= DepartmentForm(instance=department)
    context={
        'edit_department':edit_department,
        'all_department':all_department, 
        }
    return render(request, 'settings/add-edit-department.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_department']), login_url='access-denied-page')
def delete_single_department(request, department_id):
    delete_department= get_object_or_404(Department, pk=department_id)
    delete_department.delete()
    return redirect('department-settings')


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['add_tag']), login_url='access-denied-page')
def tag_settings(request):
    all_tag= Tag.objects.all().order_by('tag_priority')
    
    if request.method == 'POST':
        add_tag= TagForm(request.POST)
        if add_tag.is_valid():
            add_tag.save()
            return redirect('tag-settings')
    else:
        initial_data = {'navbar_display': True}
        add_tag= TagForm(initial=initial_data)
    context={
        'add_tag':add_tag,
        'all_tag':all_tag, 
        }
    return render(request, 'settings/add-edit-tag.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_tag']), login_url='access-denied-page')
def edit_single_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk = tag_id)
    all_tag= Tag.objects.all().order_by('tag_priority')
    
    if request.method == 'POST':
        edit_tag= TagForm(request.POST, instance=tag)
        if edit_tag.is_valid():
            edit_tag.save()
            return redirect('tag-settings')
    else:
        edit_tag= TagForm(instance=tag)
    context={
        'edit_tag':edit_tag,
        'all_tag':all_tag, 
        }
    return render(request, 'settings/add-edit-tag.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['delete_tag']), login_url='access-denied-page')
def delete_single_tag(request, tag_id):
    delete_tag= get_object_or_404(Tag, pk=tag_id)
    delete_tag.delete()
    return redirect('tag-settings')


#searching by campus
def all_paginator(club_obj, page_number, clubs_par_page):
    p = Paginator(club_obj, clubs_par_page) 
    try:
        club_obj = p.get_page(page_number) 
    except PageNotAnInteger:
        club_obj = p.page(1)
    except EmptyPage:
        club_obj = p.page(p.num_pages)
    return club_obj


# login and logout 
def loginpage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember = request.POST.get('remember_me') == 'on'  # Check if the checkbox is selected

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser or user.groups.exists():
                login(request, user)
                if remember:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER_ME)  # Set longer session cookie age
                else:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Set default session cookie age
                
                return redirect('dashboard')
            
            if user != user.is_superuser:
                login(request, user)
                if remember:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE_REMEMBER_ME)  # Set longer session cookie age
                else:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Set default session cookie age

                return redirect('dashboard')
            
        else:
            messages.success(request, ("The username and password you entered don't match. Please try again."))

    return render(request, 'login_users/login-form.html')


@login_required(login_url='login-page')
def logoutpage(request):
    logout(request)
    return redirect('index') 



@login_required(login_url='login-page')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            # messages.success(request, 'Your password has been successfully updated')
            return redirect('login-page')
        else:
            messages.error(request, 'Your password should include a mix of uppercase and lowercase letters, numbers, and symbols.')
    else:
        form = PasswordChangeForm(request.user)
    context= {'form': form}
    return render(request, 'login_users/change_password.html', context)


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_clubuser',]), login_url='access-denied-page')
def admin_changing_users_passwords(request, user_id):
    get_club= get_object_or_404(ClubUser, pk=user_id)
    if request.method == 'POST':
        password1=request.POST['password1']
        password2=request.POST['password2']
        if password1 == password2:
            get_club.password= make_password(password1)
            get_club.save()  # save the updated password to the database 
            return redirect('create-admin-user')
        else:
            messages.success(request, "Passwords you entered don't match. Please try again.")
            
    context={ 'get_club':get_club}
    return render(request, 'login_users/admin_change_password.html', context)

@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_club',]), login_url='access-denied-page')
def move_to_archive(request, pk):
    move_to_archive= get_object_or_404(Club, pk=pk)
    move_to_archive.publish= False
    move_to_archive.save()
    return redirect('archive-page')


@login_required(login_url='login-page')
@user_passes_test(lambda user: check_requested_user_permissions(user, ['change_club']), login_url='access-denied-page')
def club_publish(request, pk):
    make_publish= get_object_or_404(Club, pk=pk)
    make_publish.publish= True
    make_publish.save()
    return redirect('club-details', make_publish.permalink)


# to handel error pages 
def error_404_view(request, exception):
    return render(request, 'handler/404.html')

# to handel access denied pages 
def access_denied_page(request):
    return render(request, 'handler/access_denied_page.html')
# ----------------