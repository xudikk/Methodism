from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import models as authtoken
from datetime import timedelta, datetime
from django.conf import settings
from django.utils import timezone


from methodism import generate_key


class Otp(models.Model):
    key = models.CharField(max_length=512, unique=True)

    is_expired = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    tries = models.SmallIntegerField(default=0)
    extra = models.JSONField(default=dict)
    step = models.CharField(max_length=25, null=True)
    by = models.SmallIntegerField(choices=[
        (1, "By Register"),
        (2, "By Login"),
    ], default=1)

    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    mobile = False
    email = False

    def check_time_limit(self, time_limit=3):
        """
            created vaqtidan time_limit(3) daqiqa o'tgan yoki o'tmaganligini tekshiradi.
            Agar 3 daqiqa o'tmagan bo'lsa True, aks holda False qaytaradi.
            USE_TZ=True yoki False bo'lishidan qat'iy nazar ishlaydi.
        """
        three_minutes_later = self.created + timedelta(minutes=time_limit)
        current_time = timezone.now() if settings.USE_TZ else datetime.now()
        return current_time <= three_minutes_later

    def save(self, *args, **kwargs):
        if self.tries >= 3:
            self.is_expired = True
        if self.is_verified:
            self.is_expired = True
        return super(Otp, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.key} | {self.mobile or self.email}"

    class Meta:
        abstract = True


class Token(authtoken.Token):
    key = models.CharField(_("Key"), primary_key=True, max_length=512)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key(100)
        return super(Token, self).save(*args, **kwargs)

    class Meta:
        abstract = True
