from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeIncidentListView.as_view(), name="home"),
    path("incidents/search/", views.IncidentSearchView.as_view(), name="incident_search"),
    path("guide/", views.GuideView.as_view(), name="guide"),
    path("responders/", views.responders_view, name="responders"),
    path("stats/", views.stats_view, name="stats"),
    path("incident/new/", views.IncidentCreateView.as_view(), name="incident_new"),
    path("incident/<int:pk>/", views.IncidentDetailView.as_view(), name="incident_detail"),
    path("incident/<int:pk>/edit/", views.IncidentUpdateView.as_view(), name="incident_edit"),
    path(
        "incident/<int:pk>/delete/",
        views.IncidentDeleteView.as_view(),
        name="incident_delete",
    ),
]
