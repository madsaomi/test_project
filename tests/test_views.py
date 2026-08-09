import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestHomeView:
    def test_home_status_code(self, api_client):
        url = reverse("home")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_home_shows_vacancies(self, api_client, vacancy):
        url = reverse("home")
        response = api_client.get(url)
        assert response.status_code == 200
        assert vacancy in response.context["latest_vacancies"]


@pytest.mark.django_db
class TestVacancyListView:
    def test_vacancy_list_status(self, api_client):
        url = reverse("vacancy_list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_vacancy_list_filter(self, api_client, vacancy):
        url = reverse("vacancy_list")
        response = api_client.get(url, {"q": "Python"})
        assert response.status_code == 200

    def test_vacancy_list_search_description(self, api_client, vacancy):
        url = reverse("vacancy_list")
        response = api_client.get(url, {"q": "developer"})
        assert vacancy in response.context["vacancies"]

    def test_vacancy_list_search_no_match(self, api_client, vacancy):
        url = reverse("vacancy_list")
        response = api_client.get(url, {"q": "zzz-nonexistent"})
        assert vacancy not in response.context["vacancies"]


@pytest.mark.django_db
class TestVacancyDetailView:
    def test_vacancy_detail_status(self, api_client, vacancy):
        url = reverse("vacancy_detail", kwargs={"pk": vacancy.pk})
        response = api_client.get(url)
        assert response.status_code == 200

    def test_vacancy_detail_increments_views(self, api_client, vacancy):
        url = reverse("vacancy_detail", kwargs={"pk": vacancy.pk})
        api_client.get(url)
        vacancy.refresh_from_db()
        assert vacancy.views_count == 1


@pytest.mark.django_db
class TestDashboardRedirect:
    def test_unauthenticated_redirect(self, api_client):
        url = reverse("dashboard_redirect")
        response = api_client.get(url)
        assert response.status_code == 302

    def test_student_redirect(self, api_client, student_user):
        api_client.force_login(user=student_user)
        url = reverse("dashboard_redirect")
        response = api_client.get(url)
        assert response.status_code == 302
        assert "student" in response.url

    def test_employer_redirect(self, api_client, employer_user):
        api_client.force_login(user=employer_user)
        url = reverse("dashboard_redirect")
        response = api_client.get(url)
        assert response.status_code == 302
        assert "employer" in response.url


@pytest.mark.django_db
class TestStudentDashboard:
    def test_student_dashboard(self, api_client, student_user, student_profile):
        api_client.force_login(user=student_user)
        url = reverse("student_dashboard")
        response = api_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestEmployerDashboard:
    def test_employer_dashboard(self, api_client, employer_user, employer_profile):
        api_client.force_login(user=employer_user)
        url = reverse("employer_dashboard")
        response = api_client.get(url)
        assert response.status_code == 200
