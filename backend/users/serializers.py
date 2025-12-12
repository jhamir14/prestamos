from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Client, UserProfile

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)
    additional_info = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'photo', 'additional_info', 'is_superuser']
        read_only_fields = ['username']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        try:
            profile = instance.profile
            if profile.photo:
                request = self.context.get('request')
                if request:
                    ret['photo'] = request.build_absolute_uri(profile.photo.url)
                else:
                    ret['photo'] = profile.photo.url
            else:
                ret['photo'] = None
            ret['additional_info'] = profile.additional_info
        except UserProfile.DoesNotExist:
            ret['photo'] = None
            ret['additional_info'] = ''
        return ret

    def update(self, instance, validated_data):
        photo = validated_data.pop('photo', None)
        additional_info = validated_data.pop('additional_info', None)
        
        instance = super().update(instance, validated_data)

        profile, created = UserProfile.objects.get_or_create(user=instance)
        
        if photo is not None:
            profile.photo = photo
        
        if additional_info is not None:
            profile.additional_info = additional_info
            
        profile.save()

        return instance
