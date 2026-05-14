from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ActionLog, Incident, ResourceRequest

User = get_user_model()


class OperationsModelsAndViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(
            username="t_reporter",
            email="rep@test.local",
            password="pw123456",
        )
        cls.user_b = User.objects.create_user(
            username="t_requester",
            email="req@test.local",
            password="pw123456",
        )
        cls.user_c = User.objects.create_user(
            username="t_actor",
            email="act@test.local",
            password="pw123456",
        )
        cls.incident = Incident.objects.create(
            title="測試火警",
            category="fire",
            priority=1,
            location="測試大樓",
            description="濃煙測試描述",
            reporter=cls.user_a,
            is_active=True,
        )
        cls.rr = ResourceRequest.objects.create(
            incident=cls.incident,
            requested_by=cls.user_b,
            item_name="測試物資",
            quantity=5,
            status=ResourceRequest.STATUS_PENDING,
            is_urgent=True,
        )
        cls.log = ActionLog.objects.create(
            incident=cls.incident,
            actor=cls.user_c,
            note="測試處置：封鎖現場",
        )

    def test_incident_str(self):
        self.assertEqual(str(self.incident), "測試火警")

    def test_resource_request_str(self):
        self.assertIn("測試物資", str(self.rr))

    def test_action_log_str(self):
        self.assertIn("Log #", str(self.log))

    def test_incident_get_absolute_url(self):
        url = self.incident.get_absolute_url()
        self.assertEqual(url, reverse("incident_detail", args=[self.incident.pk]))

    def test_foreign_keys(self):
        self.assertEqual(self.incident.reporter_id, self.user_a.id)
        self.assertEqual(self.rr.requested_by_id, self.user_b.id)
        self.assertEqual(self.log.actor_id, self.user_c.id)
        self.assertEqual(self.rr.incident_id, self.incident.id)

    def test_home_path_200(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_home_reverse_200(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

    def test_home_template_and_content(self):
        resp = self.client.get(reverse("home"))
        self.assertTemplateUsed(resp, "home.html")
        self.assertContains(resp, "測試火警")

    def test_detail_path_and_reverse(self):
        resp = self.client.get(f"/incident/{self.incident.pk}/")
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.get(reverse("incident_detail", args=[self.incident.pk]))
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp2, "incident_detail.html")

    def test_detail_404(self):
        resp = self.client.get("/incident/999999/")
        self.assertEqual(resp.status_code, 404)

    def test_create_post_redirects_and_creates(self):
        reporter = User.objects.create_user("t_new_rep", "nr@test", "pw123456")
        payload = {
            "title": "新事件",
            "category": "flood",
            "priority": 2,
            "location": "河堤",
            "description": "淹水",
            "reporter": reporter.pk,
            "is_active": True,
        }
        resp = self.client.post(reverse("incident_new"), payload, follow=False)
        self.assertEqual(resp.status_code, 302)
        inc = Incident.objects.get(title="新事件")
        self.assertEqual(inc.reporter_id, reporter.pk)

    def test_update_post_changes_data(self):
        url = reverse("incident_edit", args=[self.incident.pk])
        payload = {
            "category": "medical",
            "priority": 3,
            "location": "醫務室",
            "description": "更新後描述",
            "is_active": False,
        }
        resp = self.client.post(url, payload, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.category, "medical")
        self.assertFalse(self.incident.is_active)
        self.assertEqual(self.incident.title, "測試火警")

    def test_delete_post_removes(self):
        inc = Incident.objects.create(
            title="待刪除",
            category="power",
            priority=4,
            location="電房",
            description="x",
            reporter=self.user_a,
            is_active=True,
        )
        url = reverse("incident_delete", args=[inc.pk])
        resp = self.client.post(url, follow=False)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Incident.objects.filter(pk=inc.pk).exists())

    def test_responders_page(self):
        resp = self.client.get(reverse("responders"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "t_reporter")

    def test_stats_page(self):
        resp = self.client.get(reverse("stats"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Incident 總數")

    def test_guide_page_context(self):
        resp = self.client.get(reverse("guide"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "火災應變")

    def test_search_path_reverse_template(self):
        resp = self.client.get("/incidents/search/")
        self.assertEqual(resp.status_code, 200)
        resp2 = self.client.get(reverse("incident_search"))
        self.assertEqual(resp2.status_code, 200)
        self.assertTemplateUsed(resp2, "incident_search.html")

    def test_search_q_filters(self):
        url = reverse("incident_search")
        resp = self.client.get(url, {"q": "測試火警"})
        self.assertContains(resp, "測試火警")
        resp_empty = self.client.get(url, {"q": "不存在關鍵字xyz"})
        self.assertContains(resp_empty, "查無符合條件的資料")

    def test_search_category(self):
        resp = self.client.get(reverse("incident_search"), {"category": "fire"})
        self.assertContains(resp, "測試火警")

    def test_search_priority(self):
        resp = self.client.get(reverse("incident_search"), {"priority": "1"})
        self.assertContains(resp, "測試火警")

    def test_search_is_active(self):
        resp = self.client.get(reverse("incident_search"), {"is_active": "true"})
        self.assertContains(resp, "測試火警")
        self.incident.is_active = False
        self.incident.save()
        resp2 = self.client.get(reverse("incident_search"), {"is_active": "false"})
        self.assertContains(resp2, "測試火警")

    def test_search_reporter_username(self):
        resp = self.client.get(
            reverse("incident_search"), {"reporter": self.user_a.username}
        )
        self.assertContains(resp, "測試火警")

    def test_search_rr_status_distinct(self):
        resp = self.client.get(
            reverse("incident_search"), {"rr_status": ResourceRequest.STATUS_PENDING}
        )
        self.assertContains(resp, "測試火警")

    def test_search_log_note(self):
        resp = self.client.get(reverse("incident_search"), {"log_note": "封鎖"})
        self.assertContains(resp, "測試火警")
