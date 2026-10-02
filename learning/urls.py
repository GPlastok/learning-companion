from django.urls import path

from learning import views

urlpatterns = [
    path("goals/", views.goal_list, name="goal_list"),
    path("goals/new/", views.goal_create, name="goal_create"),
    path("goals/<int:pk>/", views.goal_detail, name="goal_detail"),
    path("goals/<int:pk>/edit/", views.goal_edit, name="goal_edit"),
    path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete"),
    path(
        "goals/<int:pk>/resources/new/",
        views.resource_create,
        name="resource_create",
    ),
    path("resources/<int:pk>/edit/", views.resource_edit, name="resource_edit"),
    path("resources/<int:pk>/delete/", views.resource_delete, name="resource_delete"),
    path("sessions/", views.session_list, name="session_list"),
    path("sessions/new/", views.session_create, name="session_create"),
    path("sessions/<int:pk>/edit/", views.session_edit, name="session_edit"),
    path("sessions/<int:pk>/delete/", views.session_delete, name="session_delete"),
]
