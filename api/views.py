from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import F

from .serializers import (
    RegisterSerializer, UserSerializer, StudentProfileSerializer,
    EmployerProfileSerializer, VacancyListSerializer, VacancyDetailSerializer,
    VacancyCreateSerializer, ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationStatusSerializer, CategorySerializer,
)
from .permissions import IsStudent, IsEmployer, IsVacancyOwner
from .throttles import ApplyRateThrottle
from accounts.models import User
from profiles.models import StudentProfile, EmployerProfile
from vacancies.models import Vacancy, Category
from vacancies.filters import VacancyFilter
from applications.models import Application


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.role == "student":
            StudentProfile.objects.create(user=user)
        else:
            EmployerProfile.objects.create(user=user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# --- Vacancies ---

class VacancyListAV(generics.ListAPIView):
    queryset = Vacancy.objects.filter(is_active=True).select_related(
        "employer", "category", "employer__user"
    )
    serializer_class = VacancyListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = VacancyFilter
    ordering_fields = ["created_at", "views_count", "salary"]
    ordering = ["-created_at"]


class VacancyDetailAV(generics.RetrieveAPIView):
    queryset = Vacancy.objects.filter(is_active=True).select_related(
        "employer", "category", "employer__user"
    )
    serializer_class = VacancyDetailSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Vacancy.objects.filter(pk=instance.pk).update(views_count=F("views_count") + 1)
        instance.views_count += 1
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryListAV(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class VacancyCreateAV(generics.CreateAPIView):
    serializer_class = VacancyCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def perform_create(self, serializer):
        profile = get_object_or_404(EmployerProfile, user=self.request.user)
        serializer.save(employer=profile)


class VacancyUpdateAV(generics.UpdateAPIView):
    serializer_class = VacancyCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer, IsVacancyOwner)

    def get_queryset(self):
        return Vacancy.objects.filter(employer__user=self.request.user)


class VacancyDeleteAV(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsEmployer, IsVacancyOwner)

    def get_queryset(self):
        return Vacancy.objects.filter(employer__user=self.request.user)


# --- Profiles ---

class StudentProfileAV(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)

    def get_object(self):
        obj, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return obj


class EmployerProfileAV(generics.RetrieveUpdateAPIView):
    serializer_class = EmployerProfileSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def get_object(self):
        obj, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        return obj


# --- Applications ---

class CreateApplicationAV(generics.CreateAPIView):
    serializer_class = ApplicationCreateSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)
    throttle_classes = (ApplyRateThrottle,)

    def perform_create(self, serializer):
        student = get_object_or_404(StudentProfile, user=self.request.user)
        try:
            serializer.save(student=student)
        except IntegrityError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Вы уже откликались на эту вакансию")


class StudentApplicationsAV(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsStudent)

    def get_queryset(self):
        profile = get_object_or_404(StudentProfile, user=self.request.user)
        return Application.objects.filter(student=profile).select_related(
            "vacancy", "vacancy__employer", "vacancy__employer__user"
        )


class EmployerApplicationsAV(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer)

    def get_queryset(self):
        profile = get_object_or_404(EmployerProfile, user=self.request.user)
        return Application.objects.filter(
            vacancy__employer=profile
        ).select_related("student", "student__user", "vacancy")


class UpdateApplicationStatusAV(generics.UpdateAPIView):
    serializer_class = ApplicationStatusSerializer
    permission_classes = (permissions.IsAuthenticated, IsEmployer, IsVacancyOwner)

    def get_queryset(self):
        return Application.objects.filter(vacancy__employer__user=self.request.user)


class ApplicationDeleteAV(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == "student":
            return Application.objects.filter(student__user=user)
        return Application.objects.filter(vacancy__employer__user=user)
