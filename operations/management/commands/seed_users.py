from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from operations.models import ResponderProfile

User = get_user_model()

SEED_USERS = [
    {
        "username": "cmd_center_01",
        "email": "cmd01@rescue-center.local",
        "password": "pass12345",
        "role": ResponderProfile.ROLE_COMMAND,
    },
    {
        "username": "medical_01",
        "email": "med01@rescue-center.local",
        "password": "pass12345",
        "role": ResponderProfile.ROLE_MEDICAL,
    },
    {
        "username": "logistics_01",
        "email": "log01@rescue-center.local",
        "password": "pass12345",
        "role": ResponderProfile.ROLE_LOGISTICS,
    },
    {
        "username": "shelter_01",
        "email": "shel01@rescue-center.local",
        "password": "pass12345",
        "role": ResponderProfile.ROLE_SHELTER,
    },
]


class Command(BaseCommand):
    help = "建立管理者 ntub/123 與至少四位一般使用者（含角色資料），可重複執行。"

    def handle(self, *args, **options):
        admin = User.objects.filter(username="ntub").first()
        if admin is None:
            User.objects.create_superuser(
                username="ntub",
                email="ntub@ntub.edu.tw",
                password="123",
            )
            self.stdout.write(self.style.SUCCESS("已建立 superuser：ntub"))
        else:
            admin.email = "ntub@ntub.edu.tw"
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.set_password("123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("已更新 superuser：ntub（密碼重設為 123）"))

        for spec in SEED_USERS:
            user = User.objects.filter(username=spec["username"]).first()
            if user is None:
                user = User.objects.create_user(
                    username=spec["username"],
                    email=spec["email"],
                    password=spec["password"],
                )
            else:
                user.email = spec["email"]
                user.is_staff = False
                user.is_superuser = False
                user.is_active = True
                user.set_password(spec["password"])
                user.save()

            ResponderProfile.objects.update_or_create(
                user=user,
                defaults={"role": spec["role"]},
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"一般使用者 {user.username}（角色 {spec['role']}）已就緒"
                )
            )

        self.stdout.write(self.style.SUCCESS("seed_users 完成。"))
