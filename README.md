# <span style="color: magenta;">Methodism</span>
Methodism sizga djangoda API larni tezroq yaratish va tez ishlatish imkoni beradi.  
***Egamberdiyev Xudoyberdi Tomonidan Yaratilgan***

# O'rnatish uchun qo'llanma 
1. Virtual muhit yarating va faollashtiring:

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
```
2. Pip va setuptools ni yangilang (muhim!):
```bash
python -m pip install --upgrade pip setuptools wheel
```
3. Methodism ni o'rnating:
```bash
pip install methodism
```
Agar Python 3.12+ da muammo bo'lsa, `--no-build-isolation` flagini qo'shing:
```bash
pip install methodism --no-build-isolation
```

Talablar: Python 3.8+, Django 4.2+, djangorestframework 3.14+

## About
Ushbu Kutubxona Egamberdiyev Xudoyberdi Tomonidan yaratilgan bo'lib tog'ridan tog'ri django 
kutubxonasi ustiga qurulgan. Bu sizga API lar yozganda uni tez ishlatish va tezroq API yozish imkoni beradi.
Avtomatik tarzda siz yozgan funksiyani method ga aylantirgan holatda api hosil qiladi

### filelar
* ``methodism/costumizing.py``  ushbu file tayyor bir qator claslarni custom holarga o'tqazilgan varianti hisoblanadi.  
* ``methodism/decors.py`` Kerakli decoratorlar (``params_required``, ``public_method`` va boshqalar).
* ``methodism/error_messages.py`` bo'lishi mumkin bo'lgan xatoliklar yig'ilgan lug'at ko'rinishidagi file.   
* ``methodism/helper.py`` Yordamchi funksiyalar joylangan file.   
* ``methodism/main.py`` Asosiy classlar yozilgan file
* ``methodism/models.py`` Kerakli bo'lishi mumkin bo'lgan abstract modellar to'plami (``Token``, ``Otp``)
* ``methodism/paginator.py`` va ``methodism/sqlpaginator.py`` Ushbu fayllar bizga paginatsiya hosil qilishda yordam beradi


## Ishlatish ketma ketligi

#### Birinchi navbatda kerakli kutubxonalarni o'rnatib olishingiz kerak
#### From GitHub
```bash
pip install -r requirements.txt
```  
#### From PyPi
```bash
pip install methodism
```  

Yuklab olib bo'lgach O'zingizga  `views.py` faylida kerakli bo'lgan classni yozing va uni `urls.py` ga ulang,
class ga esa `methodism` dagi `METHODISM` classidan vorislik bering.  
### Example in `views.py`

```python
from methodism import METHODISM

# agar bundan foydalansangiz settings.INSTALLED_APPS ga 'rest_framework.authtoken' ni qo'shib qo'ying
from rest_framework.authtoken.models import Token 
from app import services


class YourClass(METHODISM):

    file = services              # yoki yo'l ko'rinishida: file = "app.services"
    get_methods = services       # faqat get methodlari uchun
    token_key = "Bearer"
    auth_headers = "Authorization"
    token_class = Token
    not_auth_methods = []        # ro'yxatdan o'tish shart bo'lmagan funksiyalarni qo'shib qo'ying ("*" - hammasi)
    
    
    """ Misol uchun yozgan funksiyangiz:
        def salom_dunyo(requests, params):
            return "salom"
        methodism:
            salom.dunyo
        
        siz yozgan har qanday ostki chiziqli yoki oddiy chiziqli funksiyalar nuqta orqali avtomatik ajratiladi!
        not_auth_methods = ['salom.dunyo']
     """
```

`urls.py`:
```python
from django.urls import path
from app.views import YourClass

urlpatterns = [
    path("api/", YourClass.as_view()),
]
```

So'rov:
```
POST /api/
Authorization: Bearer <token>
{"method": "salom.dunyo", "params": {}}

GET /api/?method=salom.dunyo
```

## Qo'shimcha sozlamalar (0.4.0 dan boshlab)

| Atribut | Default | Vazifasi |
|---|---|---|
| `token_lifetime` | `None` | Token amal qilish muddati: `timedelta(days=7)` yoki sekundlarda `int` |
| `use_http_status` | `False` | `True` bo'lsa HTTP status `status_code` ga teng bo'ladi (401, 404, 500 ...). `False` - doim 200 |
| `show_exception_details` | `None` | Xatolik tafsilotlarini javobda ko'rsatish. `None` - `settings.DEBUG` ga qarab |
| `strict_methods` | `False` | `True` bo'lsa faqat `file` ning o'zida yozilgan funksiyalar chaqiriladi (import qilinganlari emas) |
| `database` | `"default"` | (faqat `SqlAPIMethodism`) qaysi bazada sql ishlatiladi |

`settings.py` da `APP_NAME = "Loyiha nomi"` yozib qo'yishingiz mumkin - u javobdagi `"Origin"` ga chiqadi (yozilmasa `"Methodism"`).

## Decoratorlar

```python
from methodism import custom_response, params_required, public_method


@public_method                          # not_auth_methods ga yozish shart emas
@params_required("phone", "password")   # params da shu kalitlar bo'lmasa avtomatik xatolik qaytaradi
def auth_login(request, params):
    ...
    return custom_response(True, data={...})
```

## Tillar

```python
from methodism import MESSAGE, lang_helper, translate

lang = lang_helper(request)   # user.lang -> Accept-Language header -> 'en'
translate(MESSAGE['NotData'], lang)   # "Ma'lumot topilmadi" / "Информация не найдена" / ...
```

## Modellar

```python
from methodism import models


class Token(models.Token):     # 200 belgili kalit, METHODISM(token_class=Token) bilan ishlaydi
    pass


class Otp(models.Otp):
    max_tries = 3      # nechta xato urinishdan keyin yaroqsiz bo'ladi
    time_limit = 3     # necha daqiqa amal qiladi

# otp.is_valid(), otp.add_try(), otp.check_time_limit()
```

# Navbatdagi class SqlAPIMethodism

```python
from methodism import SqlAPIMethodism

# agar bundan foydalansangiz settings.INSTALLED_APPS ga 'rest_framework.authtoken' ni qo'shib qo'ying
from rest_framework.authtoken.models import Token 
from app import sql_services

class YourClass(SqlAPIMethodism):

    file = sql_services  # funksiyalar joylashgan file
    get_methods = sql_services  # faqat get methodlari uchun
    token_key = "Bearer"
    auth_headers = "Authorization"
    token_class = Token
    not_auth_methods = [] # ro'yxatdan o'tish shart bo'lmagan funksiyalarni qo'shib qo'ying
```

### funksiya taxminan shunaqa yozilishi shart!
```python
def funk(request, params):
    return "select colums from your_table", False

# funk 2ta qiymat qaytaradi: str -> sql va Bool
# True -> agar natija bitta bo'lsa
# False -> agar natija bittadan ko'p bo'lsa


# XAVFSIZ USUL: foydalanuvchidan kelgan qiymatlarni 3-qiymat sifatida bering (SQL injectiondan himoya)
def user_detail(request, params):
    return "select * from users where id = %s", True, [params["id"]]

# DIQQAT: params ni hech qachon f-string orqali sql ichiga qo'shmang!
# YOMON:  return f"select * from users where id = {params['id']}", True


# AGARDA XATOLIK QAYTARMOQCHI BO'LINSA
def funk(request, params):
    return {"error": "xatolik"}  # status=False bo'lib qaytadi
    # yoki: return custom_response(False, message="...")

# DIQQAT: GET zaprosi uchun funksiya yozilganda params kirib kelmaydi
```

### Paginatsiya
```python
from methodism.sqlpaginator import SqlPaginator

def users(request, params):
    total = ...  # select count(*) ...
    p = SqlPaginator(request, page=params.get("page"), per_page=20, count=total, max_per_page=100)
    rows = ...   # "select * from users limit %s offset %s", [p.limit, p.offset]
    return custom_response(True, data={"items": rows, **p.get_paginated_response()})
```

## Testlar
```bash
pip install -r requirements-dev.txt
python -m pytest
```

## <span style="color: orange;">Qo'shimcha ishlatishga oid qoidalarni Methodism Asosiy funksiyasiga kiritilgan documentatsiyadan ham o'rganib olish mumkin</span>

O'zgarishlar tarixi: [CHANGELOG.md](CHANGELOG.md)

---

## <span style='color: magenta;'> Kod Manbalari</span>
   * ### [GitHub](https://github.com/xudikk/Methodism)  
   * ### [PyPi](https://pypi.org/project/methodism/) 

 <span style="color: blue;">Methodism Barcha uchun ochiq kutubxona. Kodlari va yoki qo'shimcha ma'lumotlarni bemalol githubdan yoki dasturchining o'zidan so'rab o'rganib olishingiz mumkin</span>

# Happy Time. Enjoy IT ;)

###### if you can't understand contact with [programmer](https://t.me/xudikk)
