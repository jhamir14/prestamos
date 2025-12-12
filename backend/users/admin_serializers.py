from rest_framework import serializers
from django.contrib.auth.models import User

class AdminUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['superadmin', 'admin'], write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_superuser', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role', 'admin')
        password = validated_data.pop('password')
        
        if role == 'superadmin':
            user = User.objects.create_superuser(
                password=password,
                **validated_data
            )
        else:
            user = User.objects.create_user(
                password=password,
                **validated_data
            )
            user.is_staff = True
            user.save()
            
        return user
