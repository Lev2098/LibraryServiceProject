import os
import django
from dotenv import load_dotenv, set_key


load_dotenv(dotenv_path="C:/Users/lev20/PycharmProjects/LibraryServiceProject/.env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()


from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from borrowing.models import Borrowing
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не задано в .env файлі!")

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Користувач"

    # Збереження chat_id у файл .env
    set_key(".env", "TELEGRAM_CHAT_ID", str(chat_id))

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Привіт, {username}! Ваш chat_id збережено: {chat_id}"
             f""
    )
    print(f"Новий користувач: {username}, chat_id: {chat_id}")

User = get_user_model()

EMAIL = range(1)

async def check_my_borrowing_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ініціює процес перевірки позик і запитує email користувача."""
    await update.message.reply_text(
        "Будь ласка, введіть вашу електронну пошту для перевірки позик:"
    )
    return EMAIL  # Переходимо до стану очікування введення email

async def check_my_borrowing_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє введену електронну пошту і повертає список позик."""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "User"
    email = update.message.text.strip()  # Отримуємо текст повідомлення як email

    if not email:
        await update.message.reply_text(
            "Будь ласка, введіть дійсну електронну пошту."
        )
        return EMAIL

    try:
        user = await sync_to_async(User.objects.get)(email=email)
    except User.DoesNotExist:
        await update.message.reply_text(
            f"Привіт, {username}! Користувача з електронною поштою {email} не знайдено."
        )
        return ConversationHandler.END

    borrowings = await sync_to_async(list)(
        Borrowing.objects.filter(user=user).select_related("book")
    )

    if not borrowings:
        await update.message.reply_text(
            f"Привіт, {username}! У вас немає записів про позичені книги."
        )
        return ConversationHandler.END

    borrowing_list = "\n".join(
        [
            f"📚 Книга: {borrowing.book.title}\n"
            f"   📅 Дата позики: {borrowing.date_borrowed}\n"
            f"   ⏳ Очікується повернення: {borrowing.expected_return_date}\n"
            f"   ❗ Статус: {borrowing.status}\n"
            for borrowing in borrowings
        ]
    )

    await update.message.reply_text(
        f"Привіт, {username}!\nОсь список ваших позик:\n\n{borrowing_list}"
    )
    return ConversationHandler.END

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    borrowing_handler = ConversationHandler(
        entry_points=[CommandHandler("check_my_borrowing", check_my_borrowing_start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_my_borrowing_email)],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(borrowing_handler)

    print("Бот запущено.")
    application.run_polling()

if __name__ == "__main__":
    main()
