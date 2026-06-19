# 🤖 Telegram-бот ресторана — Документация

> **Автор:** Темирбек уулу Актан
> **Тема:** Разработка веб-сайта для автоматизации бронирования столиков и управления заказами в ресторане
> **Кафедра:** ПМИ

---

## 📋 Содержание

1. [Общее описание](#общее-описание)
2. [Архитектура системы](#архитектура-системы)
3. [Файлы проекта](#файлы-проекта)
4. [Настройка перед запуском](#настройка-перед-запуском)
5. [Запуск системы](#запуск-системы)
6. [Описание всех функций бота](#описание-всех-функций-бота)
7. [Описание изменений в views.py](#описание-изменений-в-viewspy)
8. [Полный сценарий работы](#полный-сценарий-работы)
9. [Структура callback_data (кнопок)](#структура-callback_data-кнопок)
10. [Возможные ошибки и решения](#возможные-ошибки-и-решения)

---

## Общее описание

Telegram-бот является частью веб-системы ресторана, реализованной на Django. Бот выполняет роль **интерактивной панели управления** для администратора ресторана прямо в Telegram-чате.

Когда клиент оформляет заказ или бронирует столик через WebApp-сайт, администратор ресторана получает в Telegram уведомление с **двумя интерактивными кнопками**: ✅ Подтвердить и ❌ Отменить. После нажатия кнопки статус автоматически обновляется в базе данных, а клиент получает мгновенное уведомление о решении.

---

## Архитектура системы

```
Клиент (Telegram WebApp)
        │
        │  POST /order/create/  или  POST /reservation/
        ▼
┌─────────────────────────────────────┐
│         Django Backend               │
│                                     │
│  1. Создаёт запись в БД (SQLite)    │
│  2. Отправляет клиенту уведомление  │
│  3. Отправляет ADMIN уведомление    │
│     + Инлайн-кнопки                 │
└─────────────────────────────────────┘
        │
        │  Telegram Bot API
        ▼
┌─────────────────────────────────────┐
│    Чат администратора в Telegram     │
│                                     │
│  📋 Новый заказ #45                 │
│  • Плов × 2 — 600 сом              │
│  💰 Итого: 600 сом                  │
│  [✅ Подтвердить] [❌ Отменить]     │
└─────────────────────────────────────┘
        │
        │  Клик на кнопку
        ▼
┌─────────────────────────────────────┐
│      runbot.py (python-telegram-bot) │
│                                     │
│  1. Принимает callback от Telegram  │
│  2. Обновляет статус в БД Django    │
│  3. Редактирует сообщение у админа  │
│  4. Отправляет клиенту уведомление  │
└─────────────────────────────────────┘
        │
        ▼
Клиент: "✅ Заказ #45 подтверждён!"
```

---

## Файлы проекта

### Созданные файлы

| Файл | Описание |
|------|----------|
| `project/management/__init__.py` | Инициализация пакета `management` |
| `project/management/commands/__init__.py` | Инициализация пакета `commands` |
| `project/management/commands/runbot.py` | **Основной файл бота** — содержит всю логику |
| `README_BOT.md` | Данная документация |

### Изменённые файлы

| Файл | Что изменено |
|------|-------------|
| `project/views.py` | Функции `tg_send` и `tg_notify_admin` получили поддержку `reply_markup`. В `create_order` и `reservation_view` добавлены инлайн-кнопки для администратора |
| `main/settings.py` | Добавлены `TELEGRAM_ADMIN_CHAT_ID` и `WEBAPP_URL` |

---

## Настройка перед запуском

Откройте файл `main/settings.py` и заполните следующие параметры:

```python
# Токен вашего Telegram-бота (получается у @BotFather)
TELEGRAM_BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# ID чата администратора ресторана в Telegram
# Узнайте свой ID, написав боту @userinfobot
TELEGRAM_ADMIN_CHAT_ID = "ВАШ_TELEGRAM_ID"

# URL сайта ресторана (для кнопки "Открыть меню" в боте)
WEBAPP_URL = "https://ваш-домен.com"
```

### Как получить TELEGRAM_ADMIN_CHAT_ID

1. Найдите в Telegram бота **@userinfobot**
2. Напишите ему `/start`
3. Бот ответит вашим ID (например: `123456789`)
4. Вставьте этот ID в `TELEGRAM_ADMIN_CHAT_ID`

---

## Запуск системы

Для полноценной работы необходимо запустить **два процесса одновременно**:

### Терминал 1 — Django-сервер (сайт ресторана)

```bash
cd restoran
python manage.py runserver
```

### Терминал 2 — Telegram-бот

```bash
cd restoran
python manage.py runbot
```

После запуска бота в терминале появится:
```
🤖 Запуск Telegram-бота ресторана...
   Режим: Long Polling
   Для остановки нажмите Ctrl+C
```

### Запуск через Docker (продакшен)

Добавьте в `docker-compose.yml` новый сервис:

```yaml
  restoran_bot:
    build:
      context: ./restoran
    container_name: restoran_bot
    command: python manage.py runbot
    volumes:
      - ./restoran:/app
    restart: always
    depends_on:
      - restoran
```

---

## Описание всех функций бота

### project/management/commands/runbot.py

---

#### `_tg_send_client(chat_id, text)`

```python
async def _tg_send_client(chat_id: str, text: str) -> None
```

**Назначение:** Асинхронная отправка HTML-сообщения клиенту ресторана через Telegram Bot API.
**Используется в:** `handle_callback` — для уведомления клиента после подтверждения/отмены заказа или брони.
**Параметры:**
- `chat_id` — Telegram ID клиента
- `text` — текст сообщения (поддерживает HTML: `<b>`, `<i>`, `<code>`)

**Особенность:** Использует `httpx.AsyncClient` вместо `requests` для неблокирующей работы в async-контексте.

---

#### `_get_order(pk)` / `_get_reservation(pk)`

```python
@sync_to_async
def _get_order(pk: int) -> Order

@sync_to_async
def _get_reservation(pk: int) -> Reservation
```

**Назначение:** Асинхронные обёртки для получения объектов из базы данных Django.

**Почему `@sync_to_async`:** Django ORM — синхронная библиотека, а бот работает в async-цикле. Декоратор позволяет вызывать синхронный код БД без блокировки event loop.

---

#### `_set_order_status(pk, status)` / `_set_reservation_status(pk, status)`

```python
@sync_to_async
def _set_order_status(pk: int, status: str) -> None

@sync_to_async
def _set_reservation_status(pk: int, status: str) -> None
```

**Назначение:** Асинхронные обёртки для обновления статуса заказа или бронирования в БД.
**Параметры status:**
- `"confirmed"` — подтверждён
- `"cancelled"` — отменён

---

#### `cmd_start(update, context)`

```python
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
```

**Назначение:** Обработчик команды `/start`. Отправляет клиенту приветственное сообщение с кнопкой для открытия WebApp-меню ресторана.

**Что делает:**
1. Берёт URL сайта из `settings.WEBAPP_URL`
2. Создаёт `InlineKeyboardMarkup` с кнопкой `WebAppInfo`
3. Отправляет сообщение с кнопкой

**Пример ответа бота:**
```
👋 Добро пожаловать в Ресторан!

Нажмите кнопку ниже, чтобы открыть меню.

[🍽 Открыть меню]
```

---

#### `handle_callback(update, context)` — главная функция

```python
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None
```

**Назначение:** Центральный обработчик всех нажатий инлайн-кнопок от администратора.

**Принцип работы:**

1. Получает `callback_data` из нажатой кнопки (например: `"order_confirm_45"`)
2. Разбирает строку по `_`: `["order", "confirm", "45"]`
3. Определяет сущность (`order` или `res`)
4. Определяет действие (`confirm` или `cancel`)
5. Извлекает ID (`45`)

**Ветка для заказа (entity = "order"):**
- Загружает заказ из БД через `_get_order(pk)`
- Устанавливает новый статус через `_set_order_status(pk, status)`
- Редактирует сообщение администратора — убирает кнопки, добавляет статус и имя администратора
- Отправляет клиенту уведомление через `_tg_send_client`

**Ветка для бронирования (entity = "res"):**
- Аналогично, но для объекта `Reservation`
- В сообщении клиенту отображается дата, номер стола и количество гостей

**Защита от повторного нажатия:** После первого нажатия кнопки сообщение редактируется и кнопки исчезают.

---

#### `Command.handle()` — Management Command

```python
class Command(BaseCommand):
    def handle(self, *args, **options) -> None
```

**Назначение:** Точка входа Django management command. Вызывается через `python manage.py runbot`.

**Что делает:**
1. Читает `TELEGRAM_BOT_TOKEN` из настроек
2. Если токен не найден — выводит ошибку и завершает работу
3. Создаёт экземпляр `Application` из `python-telegram-bot`
4. Регистрирует обработчики:
   - `CommandHandler("start", cmd_start)` — для команды `/start`
   - `CallbackQueryHandler(handle_callback)` — для всех инлайн-кнопок
5. Запускает `app.run_polling()` с `drop_pending_updates=True`

---

## Описание изменений в views.py

### tg_send — добавлена поддержка reply_markup

```python
# БЫЛО:
def tg_send(chat_id, text):
    json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

# СТАЛО:
def tg_send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
```

### tg_notify_admin — добавлена поддержка reply_markup

```python
# БЫЛО:
def tg_notify_admin(text):
    tg_send(admin_id, text)

# СТАЛО:
def tg_notify_admin(text, reply_markup=None):
    tg_send(admin_id, text, reply_markup=reply_markup)
```

### create_order — инлайн-кнопки для администратора

```python
admin_keyboard = {
    "inline_keyboard": [[
        {"text": "✅ Подтвердить", "callback_data": f"order_confirm_{order.pk}"},
        {"text": "❌ Отменить",   "callback_data": f"order_cancel_{order.pk}"},
    ]]
}
tg_notify_admin(текст_заказа, reply_markup=admin_keyboard)
```

### reservation_view — инлайн-кнопки для администратора

```python
admin_res_keyboard = {
    "inline_keyboard": [[
        {"text": "✅ Подтвердить", "callback_data": f"res_confirm_{reservation.pk}"},
        {"text": "❌ Отменить",   "callback_data": f"res_cancel_{reservation.pk}"},
    ]]
}
tg_notify_admin(текст_брони, reply_markup=admin_res_keyboard)
```

---

## Полный сценарий работы

### Сценарий 1: Клиент оформляет заказ

```
1. Клиент открывает WebApp через Telegram-бота (команда /start)
2. Выбирает блюда и нажимает "Оформить заказ"
3. Django создаёт заказ со статусом "new" в БД
4. Клиент получает в Telegram:
   "✅ Заказ #45 принят! Ожидайте подтверждения"
5. Администратор получает:
   "🔔 Новый заказ #45
    👤 Актан @aktan_user
    • Плов × 2 — 600 сом
    💰 Итого: 600 сом
    [✅ Подтвердить] [❌ Отменить]"
6. Администратор нажимает ✅ Подтвердить
7. runbot.py:
   a) Статус заказа в БД → "confirmed"
   b) Сообщение у администратора обновляется (кнопки убраны):
      "⚡️ Статус изменён: ✅ ПОДТВЕРЖДЁН  👤 Менеджер Асан"
   c) Клиент получает:
      "✅ Заказ #45 подтверждён! Мы уже начали его готовить."
```

### Сценарий 2: Клиент бронирует столик

```
1. Клиент нажимает "Забронировать стол" в WebApp
2. Заполняет форму: имя, телефон, дата, время, гости
3. Django находит свободный стол, создаёт бронь со статусом "pending"
4. Клиент получает: "✅ Бронь #12 принята! Подтвердим в течение 15 минут."
5. Администратор получает:
   "📅 Новая бронь #12
    👤 Актан 📞 +996700000000
    📅 25.06.2026 в 19:00
    🪑 Стол №3  👥 4 гост.
    [✅ Подтвердить] [❌ Отменить]"
6. Администратор нажимает ✅ Подтвердить
7. Статус брони → "confirmed"
8. Клиент получает:
   "✅ Бронь #12 подтверждена!
    📅 25.06.2026 в 19:00
    🪑 Стол №3 (до 4 мест)
    👥 Гостей: 4
    Ждём вас! 🍽"
```

---

## Структура callback_data (кнопок)

| callback_data | Описание |
|---------------|----------|
| `order_confirm_{pk}` | Подтвердить заказ с ID = pk |
| `order_cancel_{pk}` | Отменить заказ с ID = pk |
| `res_confirm_{pk}` | Подтвердить бронирование с ID = pk |
| `res_cancel_{pk}` | Отменить бронирование с ID = pk |

---

## Возможные ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `TELEGRAM_BOT_TOKEN не задан` | Пустой токен в settings.py | Заполните `TELEGRAM_BOT_TOKEN` |
| Администратор не получает уведомления | Пустой `TELEGRAM_ADMIN_CHAT_ID` | Заполните ID через @userinfobot |
| Кнопки не появляются | Бот не запущен | Запустите `python manage.py runbot` |
| `Бронирование не найдено в БД` | Запись удалена | Проверьте данные в Django Admin |
| Клиент не получает уведомления | Клиент не запускал бота | Клиент должен написать боту `/start` |

---

## Зависимости

Все зависимости прописаны в `requirements.txt`:

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| `python-telegram-bot` | 22.7 | SDK для работы с Telegram Bot API |
| `httpx` | 0.28.1 | Асинхронные HTTP-запросы в боте |
| `asgiref` | 3.11.1 | `sync_to_async` — мост между Django ORM и async-ботом |
| `Django` | 5.2.12 | Основной веб-фреймворк проекта |
