from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ResumeSerializer(serializers.Serializer):
    file_to_process = serializers.FileField()
    job_desc_name = serializers.CharField()
    job_desc_id = serializers.IntegerField()
    comp_id = serializers.CharField()
    created_by = serializers.CharField()
    profile_loc = serializers.CharField()
    
    
