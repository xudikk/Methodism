#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan


# xatolik nomlari
MESSAGE = {
    'UndefinedError': {
        "uz": "Nomalum xatolik yuz berdi",
        "ru": "Произошла неопределенная ошибка",
        "en": "Undefined error occurred",
    },
    "DataNotFull": {
        'uz': "Kerakli ma'lumotlar kiritilmagan",
        'en': "Missing data",
        "ru": "Не введена необходимая информация"
    },
    "PasswordError": {
        'uz': "Noto'g'ri parol",
        'ru': "Неверный пароль",
        'en': "Incorrect password",
    },
    "UserPasswordError": {
        'uz': "Username yoki parol noto'g'ri",
        'ru': "Неверный пароль или username",
        'en': "Incorrect password or username",
    },
    "InvalidBasicHeader1": {
        'uz': "Basic headerda xatolik | Maʼlumotlar taqdim etilmaydi",
        'ru': "Неверный базовый заголовок | Учетные данные не предоставлены",
        'en': "Invalid basic header | No credentials provided",
    },
    "InvalidBasicHeader2": {
        'uz': "Basic headerda xatolik | Hisob maʼlumotlari qatorida boʻsh joy boʻlmasligi kerak.",
        'ru': "Неверный базовый заголовок | Строка учетных данных не должна содержать пробелов.",
        'en': "Invalid basic header | Credentials string should not contain spaces.",
    },
    "InvalidBasicHeader3": {
        'uz': "Basic headerda xatolik | Maʼlumotlar base64 da to'g'ri kodlanmagan",
        'ru': "Неверный базовый заголовок | Учетные данные неправильно закодированы в base64",
        'en': "Invalid basic header | Credentials not correctly base64 encoded",
    },
    "LogedOut": {
        'uz': "User sistemadan chiqarildi",
        'ru': "Пользователь вышел из системы",
        'en': "User has been logged out",
    },
    "TokenUnUsable": {
        'uz': "Yaroqsiz Token",
        'ru': "Yaroqsiz Token",
        'en': "Yaroqsiz Token",
    },
    "user_not": {
        'uz': "Foydalanuvchi topilmadi",
        'en': "User not found",
        'ru': 'Пользователь не найден'
    },
    "AuthToken": {
        'uz': "Token aniqlanmadi",
        'ru': "Token aniqlanmadi",
        'en': "Token aniqlanmadi",
    },
    "PasswordChanged": {
        'uz': "Parol muaffaqiyatli o'zgartirildi",
        'ru': "Пароль успешно изменен",
        'en': "Password changed successfully",
    },

    "PasswordMust": {
        'uz': f"< password > to'ldirishili shart",
        'ru': f"< password > to'ldirishili shart",
        'en': f"< password > must be filled",
    },
    "ErrorMethod": {
        "uz": "Method xato",
        "ru": "Method xato",
        "en": "Invalid Method",
    },
    "NotData": {
        'uz': "Ma'lumot topilmadi",
        'en': "No information found",
        "ru": "Информация не найдена"
    },


    "MethodMust": {
        "uz": "Method bo'lishi shart",
        "ru": "Должен быть метод",
        "en": "Method must be filled"
    },

    'ParamsNotFull': {
        "uz": "< params > to'lliq emas",
        "ru": "< params> неполные",
        "en": "< params > is incomplete"
    },
    "ParamsMustList": {
        "uz": "< params > list(array) ko'rinishida bo'lishi kerak",
        "ru": "<params> должен быть в виде списка(array)",
        "en": "< params > must be in list(array) form"
    },
    "ParamsMust": {
        "uz": "< params > bo'lishi shart",
        "ru": "Должен быть < params >",
        "en": "< params > must be filled"
    },

    "ServiceDoesNotExist": {
        "uz": "Hozircha Bunday xizmat mavjud emas",
        "ru": "Эта услуга в настоящее время недоступна",
        "en": "This service is currently unavailable"
    },

    "UserSuccessDeleted": {
        'uz': "User muvoffaqiyatli o'chirib tashlandi",
        'en': "User deleted successfully",
        "ru": "User успешно удалена"
    },
    "TokenMust": {
        'uz': f"token to'ldirishili shart",
        'ru': f"токен должен быть заполнен",
        'en': f"token must be filled",
    },
    "UserDeleted": {
        'uz': f"Ushbu user active emas yoki o'chirib yuborilgan",
        'ru': f"Этот пользователь был удален",
        'en': f"This user has been deleted",
    },

    "UserAlreadyDeleted": {
        "uz": "Foydalanuvchi allaqachon o'chirib yuborilgan",
        "ru": "Пользователь уже удален",
        "en": "User Already Deleted",
    },

    "Unauthenticated": {
        'uz': "Ro'yhatdan o'tmagan",
        'en': "Unauthenticated",
        'ru': 'Неаутентифицированный'
    },
    'PermissionDenied': {
        'uz': "Sizda bu amalni bajarish uchun ruxsat yo‘q",
        'en': "You do not have permission to perform this action",
        'ru': 'У вас нет разрешения на выполнение этого действия'
    },
    "NotAuthenticated": {
        'uz': "Autorizatsiya Talab qilinadi!",
        'en': "Authorization Required!",
        'ru': 'Требуется Авторизация!'
    },

    "UserNotFound": {
        'uz': "Foydalanuvchi topilmadi",
        'ru': "Пользователь не найден",
        'en': "User Not Found",

    },
    'MethodDoesNotExist': {
        'uz': f"Bunday method topilmadi",
        'ru': f"Такой метод не найден",
        'en': f"No such method found",
    },

}


def error_msg_unfilled(require):
    return {
        'uz': f"{require} to'ldirishili shart",
        'ru': f"Должен быть {require}",
        'en': f"{require} must be filled",
    }


def error_params_unfilled(require):
    return {
        "uz": f"< params.{require} > bo'lishi shart",
        "ru": f"Должен быть < params.{require} >",
        "en": f"< params.{require} > must be filled"
    }
