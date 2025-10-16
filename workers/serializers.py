from rest_framework import serializers

from workers.models import Worker

class WorkerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'email', 'position', 'is_active']

class WorkerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'email',
               'position', 'is_active', 'hired_date', 'created_by']
        read_only_fields = ['hired_date', 'created_by']


class ImportWorkersSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text="Excel файл для импорта (.xlsx, .xls)"
    )