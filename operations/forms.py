from django import forms
from django.contrib.auth import get_user_model

from .models import Incident

User = get_user_model()


class IncidentCreateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            "title",
            "category",
            "priority",
            "location",
            "description",
            "reporter",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporter"].queryset = User.objects.filter(is_active=True).order_by(
            "username"
        )


class IncidentUpdateForm(forms.ModelForm):
    """Update form: title is not editable (excluded; show read-only in template)."""

    class Meta:
        model = Incident
        fields = ["category", "priority", "location", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
