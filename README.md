# 📚 LibraryService

**LibraryService** — це система управління бібліотекою, яка дозволяє користувачам брати книги в оренду, перевіряти стан своїх позик та сплачувати штрафи за прострочення. Проєкт включає в себе Django backend, Telegram-бота для взаємодії з користувачами, а також модуль інтеграції з платіжними системами для обробки платежів.

---

## 🚀 Основні особливості

- **Управління позиками книг:**  
  Користувачі можуть переглядати свої позики, статус книг (очікування, повернення) та оплачувати штрафи за прострочення.
  
- **Телеграм-бот:**  
  Телеграм-бот забезпечує взаємодію через чат та надає сповіщення про прострочення.

- **Платіжна система:**  
  Штрафи за прострочення можна оплатити через інтегровану платіжну систему (наприклад, Stripe, PayPal тощо).

---

## 🛠️ Стек технологій

- **Backend:** Django + DRF (Python)
- **Database:** PostgreSQL (підтримуються й інші СУБД)
- **Telegram Bot:** python-telegram-bot
- **Платіжна система:** Stripe, PayPal або інша (конфігурація залежить від проєкту)

---

## 💾 Встановлення

Дотримуйтесь наведених нижче інструкцій, щоб запустити систему локально.

### 1️⃣ Клонування репозиторію
```bash
git clone https://github.com/yourusername/LibraryService.git
cd LibraryService
```

### 2️⃣ Створення віртуального середовища
Рекомендується створити віртуальне середовище для ізоляції залежностей:
```bash
# Для Linux/macOS
python -m venv venv
source venv/bin/activate

# Для Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Встановлення залежностей
Встановіть усі необхідні пакети:
```bash
pip install -r requirements.txt
```

### 4️⃣ Налаштування змінних середовища
Створіть файл `.env` у кореневій директорії проєкту та додайте до нього такі змінні:
```env
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/your_db_name
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### 5️⃣ Міграція бази даних
Створіть таблиці в базі даних, запустивши міграції:
```bash
python manage.py migrate
```

### 6️⃣ Створення суперкористувача
Для доступу до адміністративної панелі створіть суперкористувача:
```bash
python manage.py createsuperuser
```

### 7️⃣ Запуск сервера
Запустіть сервер для перевірки роботи:
```bash
python manage.py runserver
```

### 8️⃣ Запуск Telegram-бота
Активуйте бота:
```bash
python telegram_utils/chat_id.py
```

---

## ⚙️ Використання

### Як користувач
1. Використовуйте Telegram-бота:
   - Впишіть команду `/start`, щоб почати взаємодію.
   - Відправте команду `/check_my_borrowing`, щоб отримати список своїх позик.
   - Введіть свою електронну пошту, і бот надасть:
     - список активних позик,
     - дати повернення,
     - статус (очікує повернення чи прострочено).

### Як адміністратор
1. Увійдіть в адміністративну панель за адресою:
   ```bash
   http://127.0.0.1:8000/admin/
   ```
2. Ви маєте доступ до керування:
   - користувачами,
   - книгами,
   - позиками та платежами,
   - нарахуванням штрафів.

---

## 📜 Приклади запитів

### Позики (Borrowings)
- **Перегляд усіх позик (адміністратор):**
  ```http
  GET /api/borrowings/
  ```
- **Додавання нової позики:**
  ```http
  POST /api/borrowings/add/

  {
    "user": 1,
    "book": 5,
    "expected_return_date": "2025-01-15"
  }
  ```

### Оплата (Payments)
- **Створення нового платежу:**
  ```http
  POST /api/payments/add/

  {
    "borrowing": 3,
    "payment_type": "Card",
    "status": "Pending"
  }
  ```
- **Перегляд усіх платежів (адміністратор):**
  ```http
  GET /api/payments/
  ```

---
