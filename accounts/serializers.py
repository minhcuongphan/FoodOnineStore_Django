#create userSerializer to convert user data to JSON format
from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'role', 'created_at', 'verified_at']
        read_only_fields = ['id', 'created_at', 'verified_at']