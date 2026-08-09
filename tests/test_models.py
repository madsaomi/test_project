import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_student(self):
        user = User.objects.create_user(
            email="student@test.com",
            password="pass123",
            role="student",
        )
        assert user.role == "student"
        assert user.email == "student@test.com"
        assert user.check_password("pass123")

    def test_create_employer(self):
        user = User.objects.create_user(
            email="employer@test.com",
            password="pass123",
            role="employer",
        )
        assert user.role == "employer"

    def test_username_auto_generated(self):
        user = User.objects.create_user(
            email="john@example.com",
            password="pass123",
            role="student",
        )
        assert user.username.startswith("john_")

    def test_str_representation(self):
        user = User.objects.create_user(
            email="test@test.com",
            password="pass123",
            role="student",
        )
        assert "test@test.com" in str(user)
        assert "Студент" in str(user)


@pytest.mark.django_db
class TestVacancyModel:
    def test_create_vacancy(self, vacancy):
        assert vacancy.title == "Python Developer"
        assert vacancy.is_active is True
        assert vacancy.views_count == 0

    def test_vacancy_str(self, vacancy):
        assert str(vacancy) == "Python Developer"


@pytest.mark.django_db
class TestApplicationModel:
    def test_create_application(self, application):
        assert application.status == "sent"
        assert application.cover_letter == "I am interested"

    def test_unique_together(self, student_profile, vacancy):
        from applications.models import Application
        Application.objects.create(
            vacancy=vacancy,
            student=student_profile,
            cover_letter="First",
        )
        with pytest.raises(Exception):
            Application.objects.create(
                vacancy=vacancy,
                student=student_profile,
                cover_letter="Duplicate",
            )
