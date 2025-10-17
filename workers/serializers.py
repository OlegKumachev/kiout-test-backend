from rest_framework import serializers

from workers.models import Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "position",
            "is_active",
        ]

    def validate_email(self, value):
        if Worker.objects.filter(email=value).exists():
            raise serializers.ValidationError("Worker ")
        return value


class WorkerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "position",
            "is_active",
            "hired_date",
            "created_by",
        ]
        read_only_fields = ["hired_date", "created_by"]


class ImportWorkersSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="Excel файл для импорта (.xlsx, .xls)")
