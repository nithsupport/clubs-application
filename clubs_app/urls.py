from clubs_app import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('all-clubs/', views.all_clubs, name='all-clubs'),

    #login and logout page
    path('login/', views.loginpage, name='login-page'),
    path('logout/', views.logoutpage, name='logout-page'),

    path('user/changing/password/', views.change_password, name='change-password-form'),
    # path('forget-password/', views.ForgetPassword, name='forget-password'),
    # path('reset-password/<str:token>/', views.ResetPassword, name='reset-password'),

    path('user/create/groups/', views.group_create, name='create_user_groups'),
    path('user/edit/groups/<int:group_id>/', views.group_permissions, name='edit_user_groups_form'),
    path('user/<int:user_id>/delete/', views.delete_user_from_db, name='delete-group-user'),

    # only admin can cange club password
    path('changing/password/<int:user_id>/', views.admin_changing_users_passwords, name='admin-changing-password-form'),
    path('user/create/', views.create_admin_user, name='create-admin-user'),
    path('user/edit/<int:admin_user_id>/', views.edit_admin_user, name='edit-admin-user'),


    #browse by campus, department, tag's, ribbon
    path('tag/<str:tag_permalink>/', views.brwose_tag, name="tag"),
    path('campus/<str:campus_permalink>/', views.brows_campus, name='campus'),
    path('department/<str:department_permalink>/', views.browse_department, name='department'),
    path('ribbon/<str:ribbon>/', views.brwose_ribbon, name='ribbon'),


    
    path('dashboard/campus/', views.campus_settings, name='campus-settings'),
    path('dashboard/campus/edit/<int:campus_id>/', views.edit_single_campus, name='edit-single-campus'),
    path('dashboard/campus/delete/<int:campus_id>/', views.delete_single_campus, name='delete-single-campus'),

    path('dashboard/department/', views.department_settings, name='department-settings'),
    path('dashboard/department/edit/<int:department_id>/', views.edit_single_department, name='edit-single-department'),
    path('dashboard/department/delete/<int:department_id>/', views.delete_single_department, name='delete-single-department'),

    path('dashboard/tag/', views.tag_settings, name='tag-settings'),
    path('dashboard/tag/edit/<int:tag_id>/', views.edit_single_tag, name='edit-single-tag'),
    path('dashboard/tag/delete/<int:tag_id>/', views.delete_single_tag, name='delete-single-tag'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('create-club/', views.create_account, name='create-account'),
    path('<str:club_permalink>/edit-club/', views.edit_club_account, name='edit-club-account'),
    path('edit/<str:club_permalink>/', views.user_edit_club_account, name='user-edit-club-account'),
    path('<int:club_id>/delete-club/', views.delete_club_from_db, name='delete-club-account'),
    
    path('<str:club_permalink>/award/', views.create_award, name='create-award'),
    path('<str:club_permalink>/award/<int:award_id>/edit/', views.edit_award, name='edit-award'),
    path('<str:club_permalink>/award/<int:award_id>/delete/', views.delete_award, name='delete-award'),

    path('<str:club_permalink>/member/', views.create_member, name='create-member'),
    path('<str:club_permalink>/member/<int:member_id>/edit/', views.edit_member, name='edit-member'),
    path('<str:club_permalink>/member/<int:member_id>/delete/', views.delete_member, name='delete-member'),

    path('<str:club_permalink>/staff-cordinate/', views.create_staff_co, name='create-staff-cordinate'),
    path('<str:club_permalink>/staff-cordinate/<int:staff_cordinate_id>/edit/', views.edit_staff_co, name='edit-staff-cordinate'),
    path('<str:club_permalink>/staff-cordinate/<int:staff_cordinate_id>/delete/', views.delete_staff_co, name='delete-staff-cordinate'),

    path('<str:club_permalink>/social-media/', views.add_social_media, name='add-social-media'),
    path('<str:club_permalink>/social-media/<int:social_media_id>/edit/', views.edit_social_media, name='edit-social-media'),
    path('<str:club_permalink>/social-media/<int:social_media_id>/delete/', views.delete_single_social_media, name='delete-social-media'),
    


    path('archive/list/', views.archive_page, name='archive-page'),
    path('archived/<int:pk>/', views.move_to_archive, name='move-to-archive'),
    path('publish/<int:pk>/', views.club_publish, name='publish-club'),

    path('<str:club_permalink>/members/', views.member_list, name='member-list'),
    path('<str:club_permalink>/awards/', views.award_list, name='award-list'),
    path('<str:club_permalink>/', views.club_details, name='club-details'),
    path('error/404/', views.error_404_view, name='404-error'),
    path('user/access-denied-page/', views.access_denied_page, name='access-denied-page')
]
