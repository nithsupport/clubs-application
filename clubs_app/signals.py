from .models import Club, Campus, Department, Tag, SocialMedia, StaffCordinate, Award, Member
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


# global declaration of models to access in every funtion
club_objects = Club.objects.all()
social_media_objects = SocialMedia.objects.all()
staff_cordinate_objects = StaffCordinate.objects.all()
award_objects = Award.objects.all()
member_objects = Member.objects.all()

campus_objects = Campus.objects.all()
department_objects = Department.objects.all()
tag_objects = Tag.objects.all()


# Signal handlers to update queryset objects

@receiver(post_save, sender=Club)
@receiver(post_delete, sender=Club)
def update_club_objects(sender, instance, **kwargs):
    global club_objects
    club_objects = Club.objects.all()


@receiver(post_save, sender=SocialMedia)
@receiver(post_delete, sender=SocialMedia)
def update_social_media_objects(sender, instance, **kwargs):
    global social_media_objects
    social_media_objects = SocialMedia.objects.all()


@receiver(post_save, sender=StaffCordinate)
@receiver(post_delete, sender=StaffCordinate)
def update_staff_cordinate_objects(sender, instance, **kwargs):
    global staff_cordinate_objects
    staff_cordinate_objects = StaffCordinate.objects.all()


@receiver(post_save, sender=Award)
@receiver(post_delete, sender=Award)
def update_award_objects(sender, instance, **kwargs):
    global award_objects
    award_objects = Award.objects.all()


@receiver(post_save, sender=Member)
@receiver(post_delete, sender=Member)
def update_member_objects(sender, instance, **kwargs):
    global member_objects
    member_objects = Member.objects.all()


@receiver(post_save, sender=Campus)
@receiver(post_delete, sender=Campus)
def update_campus_objects(sender, instance, **kwargs):
    global campus_objects
    campus_objects = Campus.objects.all()


@receiver(post_save, sender=Department)
@receiver(post_delete, sender=Department)
def update_department_objects(sender, instance, **kwargs):
    global department_objects
    department_objects = Department.objects.all()


@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
def update_tag_objects(sender, instance, **kwargs):
    global tag_objects
    tag_objects = Tag.objects.all()
