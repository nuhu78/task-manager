from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import Team, TeamMember

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='Phone number must be exactly 11 digits.',
)


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, validators=[phone_validator])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'bio', 'profile_picture',
                  'first_name', 'last_name', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm Password')
    phone = serializers.CharField(required=False, validators=[phone_validator])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role']


class TeamMemberSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='employee'),
        source='employee',
        write_only=True
    )

    class Meta:
        model = TeamMember
        fields = ['id', 'employee', 'employee_id', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'manager', 'members', 'member_count', 'created_at']
        read_only_fields = ['id', 'manager', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()


class TeamListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'manager', 'member_count', 'created_at']
        read_only_fields = ['id', 'manager', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()
