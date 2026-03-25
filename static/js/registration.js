const { createApp } = Vue;
const { Form, Field, ErrorMessage, defineRule } = VeeValidate;

// 1. Правила валидации
defineRule('required', (value) => !!value || 'Поле обязательно');
defineRule('phone', (value) => {
    if (!value) return true;
    // Разрешаем цифры, скобки, плюсы, тире. Минимум 10 цифр.
    const digits = value.replace(/\D/g, '');
    return digits.length >= 10 || 'Введите корректный номер (минимум 10 цифр)';
});
defineRule('digits', (value, [length]) => {
    if (!value) return true;
    return value.length == length || `Введите ${length} цифр`;
});

// 2. Создание приложения Vue
const registrationApp = createApp({
    components: {
        VForm: Form,
        VField: Field,
        ErrorMessage: ErrorMessage,
    },
    data() {
        return {
            Step: 'Number', // 'Number' или 'Code'
            RegInput: '', // То, что пользователь видит в поле
            EnteredNumber: '', // Сохраненный нормализованный номер
            isLoading: false,
            serverError: '',
            timer: '05:00',
            timerInterval: null
        };
    },
    computed: {
        // Динамическая схема валидации
        RegSchema() {
            if (this.Step === 'Number') {
                return { phone_format: 'required|phone' };
            } else {
                return { code_format: 'required|digits:6' };
            }
        }
    },
    methods: {
        // Функция получения CSRF токена из cookie (нужно для Django)
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
        },

        // Главная функция отправки формы
        async RegSubmit(values, { resetForm }) {
            console.log('--- НАЧАЛО ОТПРАВКИ ---');
            console.log('Step:', this.Step);
            console.log('Input:', this.RegInput);

            // Сбрасываем ошибку сервера
            this.serverError = '';

            // Простая проверка на пустоту
            if (!this.RegInput.trim()) {
                this.serverError = this.Step === 'Number' ? 'Введите номер' : 'Введите код';
                return;
            }

            this.isLoading = true;

            try {
                const csrftoken = this.getCookie('csrftoken');
                console.log('CSRF Token found:', !!csrftoken);

                if (this.Step === 'Number') {
                    // --- ШАГ 1: Отправка номера ---
                    
                    // НОРМАЛИЗАЦИЯ НОМЕРА (чтобы совпало с бэкендом)
                    let rawPhone = this.RegInput;
                    let cleanPhone = rawPhone.replace(/\D/g, ''); // Удаляем все нецифры
                    
                    // Если номер начинается с 8 и длина 11, меняем на 7
                    if (cleanPhone.startsWith('8') && cleanPhone.length === 11) {
                        cleanPhone = '7' + cleanPhone.slice(1);
                    }
                    // Добавляем плюс, если нет
                    if (!cleanPhone.startsWith('+')) {
                        cleanPhone = '+' + cleanPhone;
                    }
                    
                    console.log('Нормализованный номер для отправки:', cleanPhone);

                    const response = await fetch('/accounts/api/auth/request-code/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({ phone: cleanPhone })
                    });

                    const result = await response.json();
                    console.log('Ответ сервера (шаг 1):', result);

                    if (response.ok && result.status === 'success') {
                        // Успех: сохраняем именно нормализованный номер!
                        this.EnteredNumber = cleanPhone;
                        this.Step = 'Code';
                        this.RegInput = ''; // Очищаем поле для ввода кода
                        this.startTimer();
                        console.log('Переход к шагу ввода кода');
                    } else {
                        this.serverError = result.message || 'Ошибка отправки SMS';
                        console.error('Ошибка шаг 1:', this.serverError);
                    }

                } else if (this.Step === 'Code') {
                    // --- ШАГ 2: Проверка кода ---
                    console.log('Отправка кода для номера:', this.EnteredNumber);
                    
                    const response = await fetch('/accounts/api/auth/verify-code/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify({
                            phone: this.EnteredNumber, // Используем сохраненный нормализованный номер
                            code: this.RegInput
                        })
                    });

                    const result = await response.json();
                    console.log('Ответ сервера (шаг 2):', result);

                    if (response.ok && result.status === 'success') {
                        console.log('Успешная авторизация!');
                        // Показываем сообщение об успехе
                        this.RegInput = 'Регистрация успешна';
                        
                        // Перенаправление в личный кабинет через 1.5 секунды
                        setTimeout(() => {
                            // Проверяем, есть ли URL для редиректа в ответе, иначе используем хардкод
                            const redirectUrl = result.redirect_url || '/accounts/lk/';
                            console.log('Перенаправление на:', redirectUrl);
                            window.location.href = redirectUrl;
                        }, 1500);
                    } else {
                        this.serverError = result.message || 'Неверный код';
                        console.error('Ошибка шаг 2:', this.serverError);
                    }
                }
            } catch (error) {
                console.error('Сетевая ошибка:', error);
                this.serverError = 'Ошибка сети. Проверьте консоль.';
            } finally {
                this.isLoading = false;
                console.log('--- КОНЕЦ ОТПРАВКИ ---');
            }
        },

        // Возврат к шагу ввода номера
        ToRegStep1() {
            this.Step = 'Number';
            this.RegInput = this.EnteredNumber;
            this.serverError = '';
            if (this.timerInterval) clearInterval(this.timerInterval);
        },

        // Сброс и закрытие
        Reset() {
            this.Step = 'Number';
            this.RegInput = '';
            this.EnteredNumber = '';
            this.serverError = '';
            this.isLoading = false;
            if (this.timerInterval) clearInterval(this.timerInterval);
            
            // Программное закрытие Bootstrap модалки
            const modalEl = document.getElementById('RegModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
        },

        // Таймер обратного отсчета
        startTimer() {
            let time = 300; // 5 минут
            if (this.timerInterval) clearInterval(this.timerInterval);
            
            this.timerInterval = setInterval(() => {
                const minutes = Math.floor(time / 60);
                const seconds = time % 60;
                this.timer = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                time--;
                if (time < 0) {
                    clearInterval(this.timerInterval);
                    this.timer = '00:00';
                }
            }, 1000);
        }
    }
});

// Настройка делимитеров, чтобы не конфликтовать с Django {{ }}
// В вашем HTML используется [[ ... ]]
registrationApp.config.compilerOptions.delimiters = ['[[', ']]'];

// Монтируем приложение на элемент с id="RegModal"
registrationApp.mount('#RegModal');