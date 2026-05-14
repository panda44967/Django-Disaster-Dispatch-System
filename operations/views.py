from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import IncidentCreateForm, IncidentUpdateForm
from .models import ActionLog, Incident, ResourceRequest

User = get_user_model()


class HomeIncidentListView(ListView):
    model = Incident
    template_name = "home.html"
    context_object_name = "incidents"
    queryset = Incident.objects.select_related("reporter").all()


class IncidentDetailView(DetailView):
    model = Incident
    template_name = "incident_detail.html"
    context_object_name = "incident"

    def get_queryset(self):
        return (
            Incident.objects.select_related("reporter")
            .prefetch_related(
                "resource_requests__requested_by",
                "action_logs__actor",
            )
            .all()
        )


class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentCreateForm
    template_name = "incident_new.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentUpdateForm
    template_name = "incident_edit.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = "incident_delete.html"
    success_url = reverse_lazy("home")


class GuideView(TemplateView):
    template_name = "guide.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["response_plans"] = [
            {
                "title": "火災應變",
                "phases": [
                    {
                        "name": "初期通報",
                        "checks": [
                            {"text": "確認火源位置與延燒方向"},
                            {"text": "啟動建築物火警警報並通報 119"},
                        ],
                    },
                    {
                        "name": "疏散與救護",
                        "checks": [
                            {"text": "引導民眾依避難動線疏散"},
                            {"text": "清點避難所人數並回報指揮中心"},
                        ],
                    },
                ],
            },
            {
                "title": "淹水應變",
                "phases": [
                    {
                        "name": "警戒監測",
                        "checks": [
                            {"text": "監看雨量與水位感測資料"},
                            {"text": "標示淹水風險區域並廣播提醒"},
                        ],
                    },
                    {
                        "name": "物資調度",
                        "checks": [
                            {"text": "盤點沙包、抽水機與發電機存量"},
                            {"text": "依優先順序配送至避難所與關鍵設施"},
                        ],
                    },
                ],
            },
            {
                "title": "醫療緊急",
                "phases": [
                    {
                        "name": "現場處置",
                        "checks": [
                            {"text": "評估傷病患數量與檢傷分類"},
                            {"text": "建立臨時醫療站並連絡後送醫院"},
                        ],
                    },
                ],
            },
        ]
        return ctx


class IncidentSearchView(ListView):
    model = Incident
    template_name = "incident_search.html"
    context_object_name = "incidents"
    paginate_by = None

    def get_queryset(self):
        qs = Incident.objects.select_related("reporter").all()
        params = self.request.GET

        q = params.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(location__icontains=q)
                | Q(description__icontains=q)
            )

        category = params.get("category", "").strip()
        if category:
            qs = qs.filter(category=category)

        priority = params.get("priority", "").strip()
        if priority.isdigit():
            qs = qs.filter(priority=int(priority))

        is_active = params.get("is_active", "").strip()
        if is_active.lower() in ("true", "1", "yes"):
            qs = qs.filter(is_active=True)
        elif is_active.lower() in ("false", "0", "no"):
            qs = qs.filter(is_active=False)

        reporter = params.get("reporter", "").strip()
        if reporter:
            if reporter.isdigit():
                qs = qs.filter(reporter_id=int(reporter))
            else:
                qs = qs.filter(reporter__username__iexact=reporter)

        rr_status = params.get("rr_status", "").strip()
        if rr_status:
            qs = qs.filter(resource_requests__status=rr_status).distinct()

        rr_urgent = params.get("rr_urgent", "").strip()
        if rr_urgent.lower() in ("true", "1", "yes"):
            qs = qs.filter(resource_requests__is_urgent=True).distinct()

        log_note = params.get("log_note", "").strip()
        if log_note:
            qs = qs.filter(action_logs__note__icontains=log_note).distinct()

        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search"] = self.request.GET.dict()
        ctx["category_choices"] = ["fire", "flood", "medical", "power"]
        ctx["rr_status_choices"] = [
            ResourceRequest.STATUS_PENDING,
            ResourceRequest.STATUS_APPROVED,
            ResourceRequest.STATUS_DELIVERED,
        ]
        return ctx


def responders_view(request):
    general_users = (
        User.objects.filter(is_staff=False, is_superuser=False, is_active=True)
        .select_related("responder_profile")
        .order_by("date_joined")
    )
    return render(
        request,
        "responders.html",
        {
            "users": general_users,
            "user_count": general_users.count(),
        },
    )


def stats_view(request):
    incidents = Incident.objects.all()
    total_incidents = incidents.count()
    active_incidents = incidents.filter(is_active=True).count()
    closed_incidents = incidents.filter(is_active=False).count()
    rr_qs = ResourceRequest.objects.all()
    total_rr = rr_qs.count()
    urgent_rr = rr_qs.filter(is_urgent=True).count()
    total_logs = ActionLog.objects.count()
    general_user_count = User.objects.filter(
        is_staff=False, is_superuser=False, is_active=True
    ).count()

    per_incident = (
        Incident.objects.annotate(
            rr_count=Count("resource_requests"),
            log_count=Count("action_logs"),
        )
        .values("id", "title", "rr_count", "log_count")
        .order_by("-id")
    )

    return render(
        request,
        "stats.html",
        {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "closed_incidents": closed_incidents,
            "total_resource_requests": total_rr,
            "urgent_resource_requests": urgent_rr,
            "total_action_logs": total_logs,
            "general_user_count": general_user_count,
            "per_incident": list(per_incident),
        },
    )
