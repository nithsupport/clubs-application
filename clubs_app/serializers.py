from .models import Club
from rest_framework import serializers

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['club_id', 'title', 'founded_on', 'permalink', 'club_image']