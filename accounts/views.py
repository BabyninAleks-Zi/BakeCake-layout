import json
import random
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, get_user_model
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from .models import Profile, SMSCode

from orders.models import Order


User = get_user_model()


def get_user_profile(user):
    """Возвращает профиль пользователя."""
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"phone": user.username},
    )
    return profile


def send_telegram_message(chat_id, message):
    """Отправляет сообщение в Telegram"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        print("Ошибка: TELEGRAM_BOT_TOKEN не настроен!")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        result = response.json()
        
        if result.get('ok'):
            return True
        else:
            print(f"Ошибка Telegram API: {result}")
            return False
    except Exception as e:
        print(f"Исключение при отправке в Telegram: {e}")
        return False


@require_http_methods(["POST"])
def send_code(request):
    """Принимает номер, создает код, отправляет в Telegram"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        
        if not phone:
            return JsonResponse({'status': 'error', 'message': 'Введите номер'}, status=400)

        # Нормализация номера
        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) < 10:
            return JsonResponse({'status': 'error', 'message': 'Некорректный номер'}, status=400)
            
        full_phone = f"+{clean_phone}" if not clean_phone.startswith('+') else clean_phone

        # Создаем или находим пользователя
        user, created = User.objects.get_or_create(username=full_phone, defaults={'first_name': 'Клиент'})
        profile, _ = Profile.objects.get_or_create(user=user, defaults={'phone': full_phone})

        # Генерируем код
        code = f"{random.randint(100000, 999999)}"
        SMSCode.objects.create(phone=full_phone, code=code)

        # --- ЛОГИКА ОТПРАВКИ В TELEGRAM ---
        
        # 1. Проверяем, есть ли у пользователя сохраненный Chat ID
        chat_id = profile.telegram_chat_id
        
        # 2. Если Chat ID нет (пользователь первый раз), используем админский ID для тестов
        # В реальном сценарии тут должна быть логика: "Пожалуйста, напишите боту /start, чтобы привязать аккаунт"
        if not chat_id:
            chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', None)
            if not chat_id:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Telegram не настроен. Обратитесь к администратору.'
                }, status=500)
            
            # profile.telegram_chat_id = chat_id
            # profile.save()

        message = (
            f"🔐 <b>Код подтверждения для CakeBake</b>\n\n"
            f"Ваш код: <b>{code}</b>\n\n"
            f"Действует 5 минут. Не сообщайте код никому."
        )

        sent = send_telegram_message(chat_id, message)
        DEBUG = True
        if DEBUG:
            print(f"[DEV MODE] Код для {full_phone}: {code} (отправлен в чат {chat_id})")

        if not sent:
            return JsonResponse({
                'status': 'error', 
                'message': 'Не удалось отправить код в Telegram. Проверьте настройки бота.'
            }, status=503)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    except Exception as e:
        # Логируем ошибку для отладки
        import traceback
        print(f"Error in send_code: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_http_methods(["POST"])
def verify_code(request):
    """Принимает номер и код, проверяет, авторизует"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        code = data.get('code', '').strip()

        sms_obj = SMSCode.objects.filter(
            phone=phone, 
            code=code, 
            is_verified=False
        ).order_by('-created_at').first()

        if not sms_obj or sms_obj.is_expired():
            return JsonResponse({'status': 'error', 'message': 'Неверный или истекший код'}, status=400)

        sms_obj.is_verified = True
        sms_obj.save()

        user = User.objects.get(username=phone)
        login(request, user)

        redirect_url = '/accounts/lk/'

        return JsonResponse({
            'status': 'success',
            'redirect_url': redirect_url
        })

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def custom_logout(request):
    logout(request)
    return redirect('core:index')


@login_required
def lk_view(request):
    """Показывает страницу личного кабинета."""
    profile = get_user_profile(request.user)
    context = {
        "profile": profile,
    }
    return render(request, "lk.html", context)


@require_http_methods(["POST"])
def update_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Пользователь не авторизован'}, status=403)

    try:
        data = json.loads(request.body)
        
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        # 1. Обновляем стандартные поля модели User
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        
        if 'email' in data:
            user.email = data['email'].strip()

        # Сохраняем изменения в User
        user.save()

        # 2. Обновляем кастомные поля модели Profile
        if 'address' in data:
            profile.address = data['address'].strip()

        profile.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Данные успешно обновлены',
            'user': {
                'first_name': user.first_name,
                'email': user.email,
                'phone': profile.phone,
                'address': profile.address
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def orders_view(request):
    """Показывает список заказов пользователя."""
    profile = get_user_profile(request.user)
    user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')

    context = {
        'orders': user_orders,
        'profile': profile,
    }
    return render(request, 'lk-order.html', context)
