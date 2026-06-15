from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterTests(APITestCase):
    url = reverse("authentication:api-register")

    def _payload(self, **overrides):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass1!",
            "password_confirm": "StrongPass1!",
        }
        data.update(overrides)
        return data

    def test_register_returns_tokens_and_user(self):
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_register_creates_user_in_db(self):
        self.client.post(self.url, self._payload())
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_default_base_currency_is_inr(self):
        self.client.post(self.url, self._payload())
        self.assertEqual(User.objects.get(username="newuser").base_currency, "INR")

    def test_register_custom_base_currency(self):
        self.client.post(self.url, self._payload(base_currency="USD"))
        self.assertEqual(User.objects.get(username="newuser").base_currency, "USD")

    def test_register_duplicate_username_rejected(self):
        User.objects.create_user(username="newuser", email="other@example.com", password="pass")
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_rejected(self):
        User.objects.create_user(username="other", email="newuser@example.com", password="pass")
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch_rejected(self):
        response = self.client.post(self.url, self._payload(password_confirm="different"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_rejected(self):
        response = self.client.post(
            self.url, self._payload(password="short", password_confirm="short")
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    url = reverse("authentication:api-login")

    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="TestPass1!",
        )

    def test_login_with_username_returns_tokens(self):
        response = self.client.post(self.url, {"username": "loginuser", "password": "TestPass1!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "loginuser")

    def test_login_with_email_returns_tokens(self):
        response = self.client.post(self.url, {"username": "login@example.com", "password": "TestPass1!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_wrong_password_rejected(self):
        response = self.client.post(self.url, {"username": "loginuser", "password": "wrongpass"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_rejected(self):
        response = self.client.post(self.url, {"username": "nobody", "password": "TestPass1!"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_rejected(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, {"username": "loginuser", "password": "TestPass1!"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="logoutuser", email="logout@example.com", password="TestPass1!"
        )
        self.client.force_authenticate(self.user)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_logout_succeeds_with_valid_token(self):
        response = self.client.post(
            reverse("authentication:api-logout"), {"refresh": self.refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_missing_token_returns_400(self):
        response = self.client.post(reverse("authentication:api-logout"), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_invalid_token_returns_400(self):
        response = self.client.post(
            reverse("authentication:api-logout"), {"refresh": "not-a-valid-token"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("authentication:api-logout"), {"refresh": self.refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(APITestCase):
    url = reverse("authentication:api-profile")

    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="TestPass1!",
        )
        self.client.force_authenticate(self.user)

    def test_get_profile_returns_user_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profileuser")
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertIn("base_currency", response.data)

    def test_update_first_name(self):
        response = self.client.patch(self.url, {"first_name": "Jane"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")

    def test_update_base_currency(self):
        response = self.client.patch(self.url, {"base_currency": "USD"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.base_currency, "USD")

    def test_unauthenticated_access_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
