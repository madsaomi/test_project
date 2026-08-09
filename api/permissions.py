from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "employer"


class IsVacancyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "employer"):
            owner = obj.employer
        else:
            owner = obj.vacancy.employer
        return owner.user == request.user
