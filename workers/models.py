from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Worker(models.Model):
    first_name = models.CharField(max_length=50, blank=False, help_text="Введите имя")
    middle_name = models.CharField(max_length=50, blank=False, help_text= "Введите фамилию")
    last_name = models.CharField(max_length=50, blank=True, help_text="Введите отчество при наличии")
    email = models.EmailField(max_length=255, blank=False, help_text="email")
    position = models.CharField(max_length=100, blank=True, help_text="Должность")
    is_active = models.BooleanField(default=True)
    hired_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.middle_name} : {self.position}'



