// Получаем элемент, к которому будем монтировать приложение
const lkElement = document.getElementById('LK');

// Считываем данные из data-атрибутов, которые заполнил Django
// Если атрибута нет или он пуст, используем значение по умолчанию
const initialName = lkElement.dataset.userName || '';
const initialPhone = lkElement.dataset.userPhone || '';
const initialEmail = lkElement.dataset.userEmail || '';
const initialAddress = lkElement.dataset.userAddress || ''; // Новое поле

Vue.createApp({
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            Edit: false,
            // Используем переменные, полученные из HTML
            Name: initialName,
            Phone: initialPhone,
            Email: initialEmail,
            Address: initialAddress, // Новое поле
            Schema: {
                name_format: (value) => {
                    if (!value) return '⚠️ Поле не может быть пустым';
                    const regex = /^[a-zA-Zа-яА-ЯёЁ\s]+$/;
                    if (!regex.test(value)) {
                        return '⚠️ Недопустимые символы в имени';
                    }
                    return true;
                },
                phone_format: (value) => {
                    // Телефон часто делают readonly, но валидацию оставим
                    if (!value) return '⚠️ Поле не может быть пустым';
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,15}$/;
                    if (!regex.test(value)) {
                        return '⚠️ Формат телефона нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    if (!value) return '⚠️ Поле не может быть пустым';
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;
                    if (!regex.test(value)) {
                        return '⚠️ Формат почты нарушен';
                    }
                    return true;
                },
                address_format: (value) => {
                    // Простая валидация адреса (не пустой и не слишком короткий)
                    if (!value) return '⚠️ Введите адрес доставки';
                    if (value.length < 5) return '⚠️ Адрес слишком короткий';
                    return true;
                }
            }
        }
    },
    methods: {
        async ApplyChanges(values) {
            console.log("Сохранение данных:", values);
            
            const csrftoken = this.getCookie('csrftoken');

            try {
                const response = await fetch('/accounts/api/profile/update/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        first_name: values.name_format,
                        email: values.email_format,
                        address: values.address_format
                        // Телефон обычно не меняют через эту форму без SMS подтверждения
                    })
                });

                const result = await response.json();

                if (response.ok && result.status === 'success') {
                    this.Edit = false;
                    alert('Профиль успешно обновлен!');
                    
                    // Опционально: обновить локальные данные, если сервер вернул что-то новое
                    // this.Name = result.user.first_name; 
                    // this.Email = result.user.email;
                    // this.Address = result.user.address;
                } else {
                    alert('Ошибка: ' + (result.message || 'Не удалось сохранить данные'));
                }
            } catch (error) {
                console.error('Network error:', error);
                alert('Ошибка сети. Проверьте консоль разработчика.');
            }
        },

        // Вспомогательная функция для CSRF токена
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }
}).mount('#LK');