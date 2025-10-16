from django.contrib import admin
from import_export.formats import base_formats

from workers.models import Worker
from import_export.admin import ImportExportModelAdmin
from workers.resourse import WorkersResources



# class WorkerAdmin(ImportExportModelAdmin):
#     resource_class = WorkersResources
#
#     def before_import_row(self, row, **kwargs):
#         user = kwargs.get('user')
#         if user and not row.get('created_by'):
#             row['created_by'] = user.id
#         return super().before_import_row(row, **kwargs)
#
# admin.site.register(Worker, WorkerAdmin)


@admin.register(Worker)
class WorkerAdmin(ImportExportModelAdmin):
    resource_class = WorkersResources
    formats = [base_formats.XLSX, base_formats.CSV]  # ← добавить форматы

    # Админ-интерфейс
    list_display = ['first_name', 'middle_name', 'email', 'position', 'is_active', 'hired_date']
    list_filter = ['is_active', 'position', 'hired_date']
    search_fields = ['first_name', 'middle_name', 'last_name', 'email']
    list_editable = ['is_active']  # ← редактирование прямо из списка

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        """Передаем пользователя в resource"""
        kwargs = super().get_import_resource_kwargs(request, *args, **kwargs)
        kwargs['user'] = request.user
        return kwargs