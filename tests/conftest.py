import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email="test_student@example.com",
        password="testpass123",
        role="student",
        first_name="Test",
        last_name="Student",
    )


@pytest.fixture
def employer_user(db):
    return User.objects.create_user(
        email="test_employer@example.com",
        password="testpass123",
        role="employer",
        first_name="Test",
        last_name="Employer",
    )


@pytest.fixture
def student_profile(student_user):
    from profiles.models import StudentProfile
    return StudentProfile.objects.create(
        user=student_user,
        city="Tashkent",
        desired_position="Python Developer",
    )


@pytest.fixture
def employer_profile(employer_user):
    from profiles.models import EmployerProfile
    return EmployerProfile.objects.create(
        user=employer_user,
        company_name="Test Corp",
        company_description="A test company",
    )


@pytest.fixture
def category(db):
    from vacancies.models import Category
    return Category.objects.create(name="Python", slug="python")


@pytest.fixture
def vacancy(employer_profile, category):
    from vacancies.models import Vacancy
    return Vacancy.objects.create(
        employer=employer_profile,
        title="Python Developer",
        description="We need a Python developer",
        salary="1000-2000",
        city="Tashkent",
        category=category,
    )


@pytest.fixture
def application(student_profile, vacancy):
    from applications.models import Application
    return Application.objects.create(
        vacancy=vacancy,
        student=student_profile,
        cover_letter="I am interested",
    )
