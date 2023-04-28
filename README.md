# Methodism
Methodism sizga djangoda API larni tezroq yaratish va tez ishlatish imkoni beradi.  
***Egamberdiyav Xudoyberdi Tomonidan Yaratilgan***

```python
    pip install methodism
```
## About
Ushbu Kutubxona Egamberdiyev Xudoyberdi Tomonidan yaratilgan bo'lib tog'ridan tog'ri django 
kutubxonasi ustiga qurulgan. Bu sizga API lar yozganda uni tez ishlatish va tezroq API yozish imkoni beradi.
Avtomatik tarzda siz yozgan funksiyani method ga aylantirgan holatda api hosil qiladi

### filelar
* ``methodism/costumizing.py``  ushbu file tayyor bir qator claslarni custum holarga o'tqazilgan varianti hisoblandi.  
* ``methodism/decors.py`` Ushbu file kerakli bo'lgan decoratorlarni yozish uchun ishlatiluvchi file.
* ``methodism/error_messages.py`` bo'lishi mumkin bo'lgan xatoliklar yig'ilgan lug'at ko'rinishidagi file.   
* ``methodism/helper.py`` Yordamchi funksiyalar joylangan file.   
* ``methodism/main.py`` Asosiy class yozilgan file



## Ishlatish ketma ketligi

#### Birinchi navbatda kerakli kutubxonalarni o'rnatib olishingiz kerak
#### From GitHub
``` python
  pip install -r requirements.txt
```  
#### From PyPi
``` python
  pip install Django==4.2 django-rest-framework==0.1.0 djangorestframework==3.14.0
```  

Yuklab olib bo'lgach O'zingizga  `views.py` faylida kerakli bo'lgan classni yozing va uni `urls.py` ga ulang,
class ga esa `methodism/main.py` dagi `METHODIZM` classidan vorislik bering.  
### Example in `views.py`


```python
from methodism.main import METHODIZM

# agar bundan foydalansangiz settings.INSTALLED_APPS ga 'rest_framework.authtoken' ni qo'shib qo'ying
from rest_framework.authtoken.models import Token 


class YourClass(METHODIZM):

    file = '__main__'
    token_key = "Bearer"
    auth_headers = "Authorization"
    token_class = Token
    not_auth_methods = [] # ro'yxatdan o'tish shart bo'lmagan kutubxonalarni qo'shib qo'ying
    
    
    """ Misol uchun yozgan funksiyangiz:
        def salom_dunyo(requests, params):
            return "salom"
        methodizm:
            salom.dunyo
        
        siz yozgan har qanday ostki chiziqli yoki oddiy chiziqli funksiyalar nuqta orqali avtomatik ajratiladi!
        not_auth_methods = ['salom.dunyo']
     """
```

## [GitHub](https://github.com/xudikk/Methodism) Manba 
## [PyPi](https://pypi.org/project/methodism/) Manba

# Happy Time. Enjoy IT ;)


