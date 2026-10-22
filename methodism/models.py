from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import timedelta, datetime
from django.conf import settings
from django.utils import timezone


from methodism.helper import generate_key


class Otp(models.Model):
    """
    OTP (bir martalik kod) uchun abstract model.
    max_tries -> nechta xato urinishdan keyin kod yaroqsiz bo'ladi
    time_limit -> kod necha daqiqa amal qiladi
    """
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

    max_tries = 3
    time_limit = 3

    def check_time_limit(self, time_limit=None):
        """
            created vaqtidan time_limit(3) daqiqa o'tgan yoki o'tmaganligini tekshiradi.
            Agar 3 daqiqa o'tmagan bo'lsa True, aks holda False qaytaradi.
            USE_TZ=True yoki False bo'lishidan qat'iy nazar ishlaydi.
        """
        if self.created is None:
            return True
        limit = self.created + timedelta(minutes=time_limit if time_limit is not None else self.time_limit)
        current_time = timezone.now() if timezone.is_aware(self.created) else datetime.now()
        return current_time <= limit

    def is_valid(self):
        """ Kod hali ishlatilishi mumkinmi (muddati, urinishlar soni va tasdiqlanganligi tekshiriladi) """
        return not self.is_expired and not self.is_verified and self.tries < self.max_tries \
            and self.check_time_limit()

    def add_try(self, commit=True):
        """ Xato urinishlar sonini 1 taga oshiradi """
        self.tries += 1
        if commit:
            self.save()
        return self.tries

    def save(self, *args, **kwargs):
        if self.tries >= self.max_tries:
            self.is_expired = True
        if self.is_verified:
            self.is_expired = True
        return super(Otp, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.key} | {self.mobile or self.email}"

    class Meta:
        abstract = True


class Token(models.Model):
    """
    Uzunroq (200 belgili) kalitli token uchun abstract model.
    rest_framework.authtoken.models.Token bilan bir xil tuzilishga ega, shuning uchun
    METHODISM(token_class=YourToken) da bemalol ishlatish mumkin.

    EXP:
        class Token(methodism.models.Token):
            pass
    """
    key = models.CharField(_("Key"), primary_key=True, max_length=512)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='%(app_label)s_%(class)s',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    key_size = 100

    @classmethod
    def generate_key(cls):
        return generate_key(cls.key_size)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def __str__(self):
        return self.key

    class Meta:
        abstract = True
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")
