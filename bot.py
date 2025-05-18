import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from data import db_session
from handlers import start, expense, help, chart, export


def main():
    db_session.global_init("db/expenses.sqlite")

    load_dotenv()

    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("Токен бота не найден в .env файле!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CommandHandler("help", help.help_command))

    expense.register_handlers(app)
    chart.register_handlers(app)
    export.register_handlers(app)

    app.run_polling()


if __name__ == "__main__":
    main()
