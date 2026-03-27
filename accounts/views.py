import json
import random
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout, get_user_model
from django.shortcuts import redirect
from django.utils import timezone
from .models import Profile, SMSCode


User = get_user_model()


@require_http_methods(["POST"])
def send_code(request):
    """Принимает номер, создает код, возвращает успех"""
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
        user, _ = User.objects.get_or_create(username=full_phone, defaults={'first_name': 'Клиент'})
        Profile.objects.get_or_create(user=user, defaults={'phone': full_phone})

        # Генерируем код
        code = f"{random.randint(100000, 999999)}"
        SMSCode.objects.create(phone=full_phone, code=code)
        
        # ТУТ ДОЛЖНА БЫТЬ ОТПРАВКА SMS (через SMS.ru, Twilio и т.д.)
        print(f"SMS CODE FOR {full_phone}: {code}") 

        return JsonResponse({'status': 'success'})

    except Exception as e:
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