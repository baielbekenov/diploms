"""
runbot.py — Django management command для запуска Telegram-бота ресторана.

Запуск:
    python manage.py runbot

Бот выполняет следующие функции:
  1. Команда /start — отправляет кнопку для открытия WebApp-меню ресторана.
  2. Обрабатывает нажатие инлайн-кнопок от администратора:
     - order_confirm_<pk>  — подтвердить заказ
     - order_cancel_<pk>   — отменить заказ
     - res_confirm_<pk>    — подтвердить бронирование
     - res_cancel_<pk>     — отменить бронирование
  При нажатии кнопки:
     a) статус обновляется в базе данных Django
     b) сообщение администратора редактируется (кнопки убираются)
     c) клиент получает уведомление о новом статусе в Telegram
"""

import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
#  Хелпер: асинхронная отправка сообщения клиенту через requests
# ──────────────────────────────────────────────────────────────

async def _tg_send_client(chat_id: str, text: str) -> None:
    """Отправляет HTML-сообщение пользователю через Telegram Bot API."""
    import httpx
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
    except Exception as exc:
        logger.warning("Ошибка отправки клиенту: %s", exc)


# ──────────────────────────────────────────────────────────────
#  Вспомогательные DB-операции (sync → async через sync_to_async)
# ──────────────────────────────────────────────────────────────

@sync_to_async
def _get_order(pk: int):
    """Возвращает объект Order с prefetch пользователя."""
    from project.models import Order
    return Order.objects.select_related("user").get(pk=pk)


@sync_to_async
def _set_order_status(pk: int, status: str) -> None:
    """Устанавливает статус заказа в БД."""
    from project.models import Order
    Order.objects.filter(pk=pk).update(status=status)


@sync_to_async
def _get_reservation(pk: int):
    """Возвращает объект Reservation с prefetch клиента и стола."""
    from project.models import Reservation
    return Reservation.objects.select_related("customer", "table").get(pk=pk)


@sync_to_async
def _set_reservation_status(pk: int, status: str) -> None:
    """Устанавливает статус бронирования в БД."""
    from project.models import Reservation
    Reservation.objects.filter(pk=pk).update(status=status)


# ──────────────────────────────────────────────────────────────
#  Обработчик команды /start
# ──────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет приветственное сообщение с кнопкой открытия WebApp.
    WebApp URL берётся из настроек WEBAPP_URL (или задаётся дефолтный).
    """
    webapp_url = getattr(settings, "WEBAPP_URL", "https://yourdomain.com")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🍽 Открыть меню",
            web_app=WebAppInfo(url=webapp_url)
        )]
    ])

    await update.message.reply_text(
        "👋 Добро пожаловать в <b>Ресторан</b>!\n\n"
        "Нажмите кнопку ниже, чтобы открыть меню, сделать заказ или забронировать столик.",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# ──────────────────────────────────────────────────────────────
#  Обработчик инлайн-кнопок (CallbackQuery)
# ──────────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает нажатие кнопок администратором.

    Формат callback_data:
        order_confirm_<pk>   — подтвердить заказ
        order_cancel_<pk>    — отменить заказ
        res_confirm_<pk>     — подтвердить бронирование
        res_cancel_<pk>      — отменить бронирование
    """
    query = update.callback_query
    await query.answer()  # убираем «часики» у администратора

    data = query.data  # например: "order_confirm_45"
    parts = data.split("_")  # ["order", "confirm", "45"]

    if len(parts) < 3:
        logger.warning("Неизвестный callback_data: %s", data)
        return

    entity = parts[0]   # "order" или "res"
    action = parts[1]   # "confirm" или "cancel"
    try:
        pk = int(parts[2])
    except ValueError:
        logger.warning("Невалидный pk в callback_data: %s", data)
        return

    # ── Обработка ЗАКАЗА ──────────────────────────────────────
    if entity == "order":
        try:
            order = await _get_order(pk)
        except Exception:
            await query.edit_message_text(
                query.message.text + "\n\n❗️ Заказ не найден в базе данных."
            )
            return

        if action == "confirm":
            new_status = "confirmed"
            status_label = "✅ ПОДТВЕРЖДЁН"
            client_msg = (
                f"✅ <b>Заказ #{pk} подтверждён!</b>\n\n"
                f"👨‍🍳 Мы уже начали его готовить.\n"
                f"💰 Итого: {float(order.total_price or 0):.0f} сом\n"
                f"📌 Статус: Подтверждён"
            )
        elif action == "cancel":
            new_status = "cancelled"
            status_label = "❌ ОТМЕНЁН"
            client_msg = (
                f"❌ <b>Заказ #{pk} отменён.</b>\n\n"
                f"Если это ошибка — позвоните нам или оформите новый заказ."
            )
        else:
            return

        await _set_order_status(pk, new_status)

        # Редактируем сообщение администратора — убираем кнопки, добавляем статус
        original_text = query.message.text or query.message.caption or ""
        admin_name = query.from_user.full_name or query.from_user.username or "Администратор"
        await query.edit_message_text(
            text=original_text + f"\n\n⚡️ Статус изменён: <b>{status_label}</b>\n👤 {admin_name}",
            parse_mode="HTML",
        )

        # Уведомляем клиента
        if order.user and order.user.telegram_id:
            await _tg_send_client(order.user.telegram_id, client_msg)

    # ── Обработка БРОНИРОВАНИЯ ────────────────────────────────
    elif entity == "res":
        try:
            reservation = await _get_reservation(pk)
        except Exception:
            await query.edit_message_text(
                query.message.text + "\n\n❗️ Бронирование не найдено в базе данных."
            )
            return

        dt = reservation.reservation_time.strftime("%d.%m.%Y в %H:%M")

        if action == "confirm":
            new_status = "confirmed"
            status_label = "✅ ПОДТВЕРЖДЕНА"
            client_msg = (
                f"✅ <b>Бронь #{pk} подтверждена!</b>\n\n"
                f"📅 {dt}\n"
                f"🪑 Стол №{reservation.table.number} (до {reservation.table.seats} мест)\n"
                f"👥 Гостей: {reservation.guests_count}\n\n"
                f"Ждём вас! 🍽"
            )
        elif action == "cancel":
            new_status = "cancelled"
            status_label = "❌ ОТМЕНЕНА"
            client_msg = (
                f"❌ <b>Бронь #{pk} отменена.</b>\n\n"
                f"📅 {dt}\n"
                f"Для нового бронирования воспользуйтесь приложением."
            )
        else:
            return

        await _set_reservation_status(pk, new_status)

        # Редактируем сообщение администратора
        original_text = query.message.text or ""
        admin_name = query.from_user.full_name or query.from_user.username or "Администратор"
        await query.edit_message_text(
            text=original_text + f"\n\n⚡️ Статус изменён: <b>{status_label}</b>\n👤 {admin_name}",
            parse_mode="HTML",
        )

        # Уведомляем клиента
        if reservation.customer and reservation.customer.telegram_id:
            await _tg_send_client(reservation.customer.telegram_id, client_msg)

    else:
        logger.warning("Неизвестный тип сущности в callback: %s", entity)


# ──────────────────────────────────────────────────────────────
#  Django Management Command
# ──────────────────────────────────────────────────────────────

class Command(BaseCommand):
    """
    Django management command: python manage.py runbot

    Запускает Telegram-бота в режиме long-polling.
    Бот работает в фоновом процессе и обрабатывает входящие callback-запросы
    от инлайн-кнопок в сообщениях администратора.
    """

    help = "Запустить Telegram-бота для обработки заказов и бронирований ресторана"

    def handle(self, *args, **options) -> None:
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
        if not token:
            self.stderr.write(
                self.style.ERROR(
                    "Ошибка: TELEGRAM_BOT_TOKEN не задан в settings.py"
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("🤖 Запуск Telegram-бота ресторана..."))
        self.stdout.write(f"   Режим: Long Polling")
        self.stdout.write(f"   Для остановки нажмите Ctrl+C\n")

        # Строим приложение
        app = (
            Application.builder()
            .token(token)
            .build()
        )

        # Регистрируем обработчики
        app.add_handler(CommandHandler("start", cmd_start))
        app.add_handler(CallbackQueryHandler(handle_callback))

        # Запускаем long-polling (блокирует поток до Ctrl+C)
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,   # игнорируем накопившиеся нажатия при перезапуске
        )

        self.stdout.write(self.style.SUCCESS("Бот остановлен."))
