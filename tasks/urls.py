from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # 👈 ADD THIS
    path("analyze/", views.analyze_tasks, name="analyze_tasks"),
    path("suggest/", views.suggest_tasks, name="suggest_tasks"),
]
