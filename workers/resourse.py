import logging

from django.contrib.auth.models import User
from import_export import resources

from workers.models import Worker

logger = logging.getLogger(__name__)


class WorkersResources(resources.ModelResource):
    class Meta:
        model = Worker
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "position",
            "is_active",
        )
        import_id_fields = ["email"]

    def before_import_row(self, row, **kwargs):
        user = kwargs.get("user") or getattr(self, "user", None)
        if user:
            row["created_by"] = user.id
        else:
            # Fallback
            user = User.objects.first()
            if user:
                row["created_by"] = user.id

        logger.info(f"Импорт сотрудника: {row.get('first_name')} {row.get('email')}")
