# O'zgarishlar tarixi

## 0.4.0

### Tuzatilgan xatoliklar
* `methodism.models` import qilinganda `FieldError` berardi (`Token` modeli DRF ning konkret
  `Token` modelidan meros olib, `key` maydonini qayta e'lon qilgan edi). Endi `Token` mustaqil abstract model.
* `settings.APP_NAME` yozilmagan bo'lsa `custom_response` `AttributeError` berardi. Endi default `"Methodism"`.
* `BearerAuth` mavjud bo'lmagan `MESSAGE['UserNot']` kalitini ishlatardi (`KeyError`) va userda
  `deleted` maydoni bo'lmasa yiqilardi. Token bazadan 2 marta olinardi.
* GET funksiya `list` qaytarsa `UndefinedError` chiqardi.
* `exception_data` sinf nomini buzib ko'rsatardi (`str.strip` belgilar to'plamini olib tashlaydi:
  `accounts.Error` -> `ounts.Error`). Endi xatolik yuz bergan aniq qator va funksiya ko'rsatiladi.
* `method` ham, `params` ham yo'q bo'lsa noto'g'ri xabar chiqardi. Body JSON array bo'lsa 500 xatolik berardi.
* `not_auth_methods = ['salom.dunyo']` yozilganda `salom_dunyo` / `salom-dunyo` ko'rinishidagi
  chaqiruvlar uchun avtorizatsiya talab qilinardi. Endi barcha variantlar bir xil ishlaydi.
* `SqlAPIMethodism` da `{"error": ...}` qaytarilganda `status: True` chiqardi.
* `SqlPaginator` noto'g'ri `page` (masalan `"abc"`) berilganda yiqilardi.
* PyPI ga chiqarish workflowi ishlamasdi: `pyproject.toml` `.gitignore` da edi, `environment: pypi`
  esa `env` ichiga noto'g'ri yozilgan edi.
* Eski `setup.cfg` olib tashlandi: u `pyproject.toml` bilan to'qnashib, paket metadata'siga
  noto'g'ri (Apache) litsenziya va eski URL qo'shardi. `LICENSE` (MIT) fayli qo'shildi.
* Rus/ingliz tarjimalari yo'q xabarlar to'ldirildi.

### Xavfsizlik
* `_` bilan boshlanuvchi nomlar (`__dict__`, `_secret` ...), modullar va classlar API orqali chaqirilmaydi.
* Faol bo'lmagan (`is_active=False`) foydalanuvchilar endi token bilan kira olmaydi.
* Production da (`DEBUG=False`) xatolik tafsilotlari (fayl yo'li, qator) javobda ko'rsatilmaydi,
  lekin `methodism` logger orqali yoziladi. `show_exception_details = True` bilan yoqish mumkin.
* Ro'yxatdan o'tmagan foydalanuvchi qaysi methodlar mavjudligini bila olmaydi (avval avtorizatsiya tekshiriladi).
* `SqlAPIMethodism` parametrli so'rovlarni qo'llaydi: `return sql, True, [params]` (SQL injectiondan himoya).

### Yangi imkoniyatlar
* `token_lifetime` - token amal qilish muddati.
* `use_http_status` - HTTP status kodini javobdagi `status_code` ga moslash.
* `strict_methods` - faqat `file` ning o'zida yozilgan funksiyalarni chaqirish.
* `file` / `get_methods` ga modul yo'lini satr ko'rinishida berish mumkin: `file = "app.services"`.
* `SqlAPIMethodism.database` - boshqa bazada ishlash.
* `@params_required(...)` va `@public_method` decoratorlari.
* `lang_helper` endi `Accept-Language` headerini ham tushunadi, yangi `translate()` helper.
* `auto_dict()` - model objectini xavfsiz dict ga aylantirish (password hech qachon chiqmaydi).
* `Otp.max_tries`, `Otp.time_limit`, `Otp.is_valid()`, `Otp.add_try()`.
* `SqlPaginator.limit`, `.offset`, `max_per_page`, javobda `num_pages`.
* `BaseMethodism` - o'z classingizni yaratish uchun asos (`process_result`, `authenticate_request` va
  boshqa metodlarni qayta yozish mumkin).
* 35 ta avtomatik test va GitHub Actions orqali tekshiruv.

### E'tibor bering (xatti-harakat o'zgarishlari)
* Xatolik javoblarida `status_code` endi haqiqiy kodni ko'rsatadi (400/401/403/404/500).
  HTTP status esa avvalgidek 200 (agar `use_http_status = True` qilinmasa).
* `DEBUG=False` da xatolik javobining `data` maydoni `null` bo'ladi.
* Django 4.2+ va djangorestframework 3.14+ talab qilinadi.
