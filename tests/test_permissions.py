import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAPIPermissions:
    def test_vacancy_list_public(self, api_client, vacancy):
        url = reverse("api_vacancy_list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_vacancy_detail_public(self, api_client, vacancy):
        url = reverse("api_vacancy_detail", kwargs={"pk": vacancy.pk})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_vacancy_create_requires_auth(self, api_client):
        url = reverse("api_vacancy_create")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == 401

    def test_student_cannot_create_vacancy(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_vacancy_create")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == 403

    def test_employer_can_create_vacancy(self, api_client, employer_user, employer_profile, category):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_vacancy_create")
        data = {"title": "Test", "description": "Desc", "category": category.pk}
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201

    def test_employer_cannot_update_others_vacancy(self, api_client, vacancy, employer_user, employer_profile):
        from profiles.models import EmployerProfile
        other_employer = EmployerProfile.objects.create(
            user__email="other@test.com",
            user__role="employer",
            company_name="Other",
        )
        api_client.force_authenticate(user=other_employer.user)
        url = reverse("api_vacancy_update", kwargs={"pk": vacancy.pk})
        response = api_client.patch(url, {"title": "Hacked"}, format="json")
        assert response.status_code == 404

    def test_student_cannot_update_vacancy(self, api_client, vacancy, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_vacancy_update", kwargs={"pk": vacancy.pk})
        response = api_client.patch(url, {"title": "Hacked"}, format="json")
        assert response.status_code == 403

    def test_student_can_create_application(self, api_client, student_user, student_profile, vacancy):
        api_client.force_authenticate(user=student_user)
        url = reverse("api_create_application")
        data = {"vacancy": str(vacancy.pk), "cover_letter": "Hi"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201

    def test_employer_cannot_create_application(self, api_client, employer_user, vacancy):
        api_client.force_authenticate(user=employer_user)
        url = reverse("api_create_application")
        data = {"vacancy": str(vacancy.pk)}
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
