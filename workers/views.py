import logging

import tablib
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from workers.models import Worker
from workers.permissions import IsAdminOrReadOnly
from workers.resourse import WorkersResources
from workers.serializers import WorkerDetailSerializer, WorkerSerializer

logger = logging.getLogger(__name__)


class WorkersViewSet(ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id", "is_active", "position"]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WorkerDetailSerializer
        return WorkerSerializer

    def perform_create(self, serializer):
        worker = serializer.save(created_by=self.request.user)
        logger.info(
            f"Создан новый сотрудник: {worker.first_name} {worker.middle_name} "
            f"({worker.email}) пользователем {self.request.user.username}"
        )

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Excel file (.xlsx, .xls)",
                    }
                },
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "imported": {"type": "integer"},
                    "updated": {"type": "integer"},
                    "errors": {"type": "integer"},
                    "total": {"type": "integer"},
                },
                "example": {
                    "success": True,
                    "imported": 5,
                    "updated": 2,
                    "errors": 0,
                    "total": 7,
                },
            },
            400: {
                "type": "object",
                "properties": {"error": {"type": "string"}},
                "example": {"error": "Файл не предоставлен"},
            },
        },
        methods=["POST"],
    )
    @action(
        detail=False, methods=["post"], url_path="import", url_name="import-workers"
    )
    def import_workers(self, request):
        logger.info(f"Пользователь {request.user.username} запустил импорт Excel")

        if "file" not in request.FILES:
            return Response(
                {"error": "Файл не предоставлен"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        try:
            resource = WorkersResources()

            dataset = tablib.Dataset()

            if file.name.endswith(".xlsx"):
                dataset.load(file.read(), format="xlsx")
            elif file.name.endswith(".xls"):
                dataset.load(file.read(), format="xls")
            else:
                logger.error(f"Неподдерживаемый формат файла: {file.name}")
                return Response(
                    {"error": "Поддерживаются только .xlsx и .xls файлы"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = resource.import_data(
                dataset,
                dry_run=False,
                raise_errors=False,
                user=request.user,
            )
            logger.info(f"Импорт завершен: {result.totals}")
            response_data = {
                "success": True,
                "imported": result.totals.get("new", 0),
                "updated": result.totals.get("update", 0),
                "errors": result.totals.get("error", 0),
                "total": result.total_rows,
            }

            return Response(response_data)

        except Exception as e:
            logger.exception(f"Ошибка обработки файла {file.name}: {e}")
            return Response(
                {"error": f"Ошибка обработки файла: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
