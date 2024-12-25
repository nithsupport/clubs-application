from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from clubs_app.models import ClubUser, Club, Award, Member, StaffCordinate, SocialMedia, Tag, Department, Campus 

# Register your models here.
# class ClubUserAdmin(UserAdmin):
#     def has_module_permission(self, request):
#         return request.user.is_superuser

#     def has_view_permission(self, request, obj=None):
#         return request.user.is_superuser

#     def has_add_permission(self, request):
#         return request.user.is_superuser

#     def has_change_permission(self, request, obj=None):
#         return request.user.is_superuser

#     def has_delete_permission(self, request, obj=None):
#         return request.user.is_superuser

# admin.site.register(ClubUser, ClubUserAdmin)
admin.site.register(ClubUser)
admin.site.register(Club),
admin.site.register(SocialMedia),
admin.site.register(Award),
admin.site.register(Member),
admin.site.register(StaffCordinate),
admin.site.register(Tag),
admin.site.register(Department),
admin.site.register(Campus),