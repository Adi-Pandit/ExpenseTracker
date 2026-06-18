from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from expense.currency import normalize_currency_code
from expense.services import recalculate_user_expenses_to_base_currency

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "base_currency"]
        read_only_fields = ["id"]

    def validate_base_currency(self, value):
        return normalize_currency_code(value)

    def update(self, instance, validated_data):
        previous_base_currency = instance.base_currency
        instance = super().update(instance, validated_data)
        if instance.base_currency != previous_base_currency:
            recalculate_user_expenses_to_base_currency(instance)
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "base_currency",
        ]

    def validate_base_currency(self, value):
        return normalize_currency_code(value)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            login_username = username
            if "@" in username:
                try:
                    login_username = User.objects.get(email__iexact=username).username
                except User.DoesNotExist as exc:
                    raise serializers.ValidationError("Invalid credentials") from exc

            user = authenticate(username=login_username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data["user"] = user
        else:
            raise serializers.ValidationError("Must include username and password")

        return data


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": "Passwords don't match."})
        return data

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
