from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешаем:
    - SAFE_METHODS (GET, HEAD, OPTIONS) всем аутентифицированным пользователям
    - Запись (POST, PUT, PATCH, DELETE) только staff
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_staff


# class IsAdminOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         # Пользователь должен быть аутентифицирован
#         if not request.user or not request.user.is_authenticated:
#             return False
#
#         # Безопасные методы доступны всем авторизованным
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         # А изменение данных — только для staff
#         return request.user.is_staff
