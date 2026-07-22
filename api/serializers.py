from rest_framework import serializers
from accounts.models import User
from profiles.models import StudentProfile, EmployerProfile
from vacancies.models import Vacancy, Category
from applications.models import Application


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "first_name", "last_name", "avatar")
        read_only_fields = ("id", "email", "role")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password", "role", "first_name", "last_name")

    def validate_role(self, value):
        if value not in ("student", "employer"):
            raise serializers.ValidationError("Роль должна быть student или employer")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "id", "email", "first_name", "last_name", "city", "resume", "resume_text",
            "skills", "education", "experience", "telegram", "linkedin",
            "github", "portfolio", "desired_position", "languages",
        )


class EmployerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)

    class Meta:
        model = EmployerProfile
        fields = (
            "id", "email", "first_name", "company_name", "company_description",
            "company_logo", "website",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class VacancyListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="employer.company_name")
    company_logo = serializers.ImageField(source="employer.company_logo")
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Vacancy
        fields = (
            "id", "title", "company_name", "company_logo", "city",
            "salary", "work_type", "category_name", "created_at",
        )


class VacancyDetailSerializer(serializers.ModelSerializer):
    employer = EmployerProfileSerializer()
    category = CategorySerializer()

    class Meta:
        model = Vacancy
        fields = (
            "id", "title", "description", "requirements", "conditions",
            "salary", "city", "work_type", "category", "employer",
            "is_active", "views_count", "created_at", "updated_at",
        )
        read_only_fields = ("id", "views_count", "created_at", "updated_at")


class VacancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = (
            "title", "description", "requirements", "conditions",
            "salary", "city", "work_type", "category", "is_active",
        )


class ApplicationSerializer(serializers.ModelSerializer):
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(source="vacancy.employer.company_name", read_only=True)
    student_name = serializers.CharField(source="student.user.get_full_name", read_only=True)
    student_email = serializers.EmailField(source="student.user.email", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id", "vacancy", "vacancy_title", "company_name",
            "student_name", "student_email", "status", "cover_letter", "created_at",
        )
        read_only_fields = ("id", "status", "created_at")


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("vacancy", "cover_letter")

    def validate(self, data):
        request = self.context.get("request")
        if request and request.user.role != "student":
            raise serializers.ValidationError("Только студенты могут откликаться")
        return data


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("status",)
