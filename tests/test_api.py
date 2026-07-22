import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestRegisterAPI:
    def test_register_student(self, api_client):
        url = reverse("api_register")
        data = {
            "email": "new@student.com",
            "password": "strongpass123",
            "role": "student",
            "first_name": "New",
            "last_name": "Student",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == "student"

    def test_register_employer(self, api_client):
        url = reverse("api_register")
        data = {
            "email": "new@employer.com",
            "password": "strongpass123",
            "role": "employer",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_invalid_role(self, api_client):
        url = reverse("api_register")
        data = {
            "email": "test@test.com",
            "password": "strongpass123",
            "role": "admin",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        url = reverse("api_register")
        data = {
            "email": "test@test.com",
            "password": "short",
            "role": "student",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVacancyAPI:
    def test_list_vacancies(self, api_client, vacancy):
        url = reverse("api_vacancy_list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_vacancy_detail(self, api_client, vacancy):
        url = reverse("api_vacancy_detail", kwargs={"pk": vacancy.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Python Developer"

    def test_create_vacancy_requires_auth(self, api_client):
        url = reverse("api_vacancy_create")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_vacancy_requires_employer(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_vacancy_create")
        data = {
            "title": "New Vacancy",
            "description": "Description",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_vacancy_as_employer(self, api_client, employer_user, employer_profile, category):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_vacancy_create")
        data = {
            "title": "New Vacancy",
            "description": "Description",
            "category": category.pk,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_vacancy_owner_only(self, api_client, vacancy, employer_user):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_vacancy_update", kwargs={"pk": vacancy.pk})
        data = {"title": "Updated Title"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_vacancy(self, api_client, vacancy, employer_user):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_vacancy_delete", kwargs={"pk": vacancy.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestApplicationAPI:
    def test_create_application(self, api_client, student_user, student_profile, vacancy):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_create_application")
        data = {
            "vacancy": str(vacancy.pk),
            "cover_letter": "I am interested",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_duplicate_application_rejected(self, api_client, student_user, application):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_create_application")
        data = {
            "vacancy": str(application.vacancy.pk),
            "cover_letter": "Again",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_student_applications_list(self, api_client, student_user, application):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_student_applications")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_employer_applications_list(self, api_client, employer_user, application):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_employer_applications")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_update_application_status(self, api_client, employer_user, application):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_update_application_status", kwargs={"pk": application.pk})
        data = {"status": "viewed"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_application(self, api_client, student_user, application):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_delete_application", kwargs={"pk": application.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestProfileAPI:
    def test_student_profile(self, api_client, student_user, student_profile):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_student_profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "Tashkent"

    def test_employer_profile(self, api_client, employer_user, employer_profile):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_employer_profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["company_name"] == "Test Corp"

    def test_me_endpoint(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_me")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "test_student@example.com"
