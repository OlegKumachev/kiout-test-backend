from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats

from workers.models import Worker
from workers.resourse import WorkersResources


@admin.register(Worker)
class WorkerAdmin(ImportExportModelAdmin):
    resource_class = WorkersResources
    formats = [base_formats.XLSX, base_formats.CSV]

    list_display = [
        "first_name",
        "middle_name",
        "email",
        "position",
        "is_active",
        "hired_date",
    ]
    list_filter = ["is_active", "position", "hired_date"]
    search_fields = ["first_name", "middle_name", "last_name", "email"]
    list_editable = ["is_active"]

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_import_resource_kwargs(request, *args, **kwargs)
        kwargs["user"] = request.user
        return kwargs
