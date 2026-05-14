"""
選用：建立示範 Incident / ResourceRequest / ActionLog，方便助教驗收 db.sqlite3。
正式流程仍建議先 seed_users，再於 admin 建立事件資料；若資料庫為空可執行本指令快速還原示範資料。
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from operations.models import ActionLog, Incident, ResourceRequest

User = get_user_model()


class Command(BaseCommand):
    help = "建立示範災害事件與關聯資料（分配給不同使用者）。"

    def handle(self, *args, **options):
        if Incident.objects.exists():
            self.stdout.write("已有 Incident 資料，略過 seed_demo_data。")
            return

        if (
            User.objects.filter(username="cmd_center_01").count() == 0
            or User.objects.filter(username="medical_01").count() == 0
        ):
            self.stdout.write(
                self.style.ERROR("請先執行 python manage.py seed_users")
            )
            return

        u_cmd, u_med, u_log, u_shel = (
            User.objects.get(username="cmd_center_01"),
            User.objects.get(username="medical_01"),
            User.objects.get(username="logistics_01"),
            User.objects.get(username="shelter_01"),
        )

        specs = [
            {
                "title": "校園大樓火警通報",
                "category": "fire",
                "priority": 1,
                "location": "圖書館 3F",
                "description": "偵煙器作動，現場有濃煙。",
                "reporter": u_cmd,
                "is_active": True,
            },
            {
                "title": "地下室淹水警戒",
                "category": "flood",
                "priority": 2,
                "location": "地下停車場 B1",
                "description": "豪雨導致排水不及，積水上升中。",
                "reporter": u_med,
                "is_active": True,
            },
            {
                "title": "大型活動人員不適",
                "category": "medical",
                "priority": 3,
                "location": "體育館主場",
                "description": "多名觀眾疑似中暑，需醫療支援。",
                "reporter": u_log,
                "is_active": False,
            },
            {
                "title": "校區大範圍斷電",
                "category": "power",
                "priority": 2,
                "location": "教學一館至三館",
                "description": "變電箱異常，部分區域停電。",
                "reporter": u_shel,
                "is_active": True,
            },
        ]

        incidents = []
        for spec in specs:
            inc = Incident.objects.create(**spec)
            incidents.append(inc)

        rr_specs = [
            (0, u_med, "防火毯", 20, ResourceRequest.STATUS_PENDING, True),
            (0, u_log, "手持無線電", 10, ResourceRequest.STATUS_APPROVED, False),
            (1, u_cmd, "抽水機", 3, ResourceRequest.STATUS_PENDING, True),
            (1, u_shel, "沙包", 50, ResourceRequest.STATUS_DELIVERED, False),
            (2, u_shel, "生理食鹽水", 100, ResourceRequest.STATUS_APPROVED, True),
            (2, u_cmd, "擔架", 6, ResourceRequest.STATUS_PENDING, False),
            (3, u_med, "發電機油料", 200, ResourceRequest.STATUS_PENDING, True),
            (3, u_log, "延長線與照明", 30, ResourceRequest.STATUS_DELIVERED, False),
        ]

        for idx, requested_by, item, qty, status, urgent in rr_specs:
            ResourceRequest.objects.create(
                incident=incidents[idx],
                requested_by=requested_by,
                item_name=item,
                quantity=qty,
                status=status,
                is_urgent=urgent,
            )

        log_specs = [
            (0, u_log, "已完成初期區域封鎖與電源切斷。"),
            (0, u_shel, "避難所已預留 50 床位並完成清點。"),
            (1, u_cmd, "指揮中心已通知水利單位支援抽水。"),
            (1, u_med, "醫療站待命，準備後送機制。"),
            (2, u_cmd, "活動主辦單位已暫停進場 30 分鐘。"),
            (2, u_shel, "避難所開放冷氣與飲水供民眾休息。"),
            (3, u_med, "機電人員到場檢測變壓設備。"),
            (3, u_cmd, "已調度臨時發電車至教學一館。"),
        ]

        for idx, actor, note in log_specs:
            log = ActionLog(incident=incidents[idx], actor=actor, note=note)
            log.save()

        self.stdout.write(self.style.SUCCESS("seed_demo_data：已建立示範事件與關聯資料。"))
