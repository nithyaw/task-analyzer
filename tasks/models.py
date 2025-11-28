from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.IntegerField(default=1)
    importance = models.IntegerField(default=5)  # 1–10 scale
    dependencies = models.JSONField(default=list, blank=True)  # store list of IDs

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title