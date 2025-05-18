from telegram.ext import (ConversationHandler, CommandHandler,
                          CallbackQueryHandler)
from sqlalchemy.orm import joinedload
import datetime
from data import db_session
from data.expenses import Expense
from utils.exporter import export_expenses_to_excel
from handlers.start import menu_keyboard
from handlers.common import (EXPORT_PERIOD, cancel_keyboard,
                             period_names, get_inline_keyboard)


async def export_start(update, context):
    keyboard = get_inline_keyboard("export")
    await update.message.reply_text("Выберите период для экспорта в Excel:", reply_markup=keyboard)


async def export_button_handler(update, context):
    query = update.callback_query
    await query.answer()
    period = query.data.split("_")[1]
    period_ru = period_names[period]

    now = datetime.datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - datetime.timedelta(days=7)
    else:
        start = now - datetime.timedelta(days=30)

    session = db_session.create_session()
    expenses = (
        session.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.user_id == query.from_user.id, Expense.date >= start)
        .all()
    )
    session.close()

    if not expenses:
        await query.message.edit_text("Нет данных за выбранный период.", reply_markup=get_inline_keyboard("export"))
        return

    export_data = []
    for e in expenses:
        export_data.append({
            "date": e.date.strftime("%Y-%m-%d"),
            "amount": e.amount,
            "category_name": e.category.name if e.category else "",
            "comment": e.comment or ""
        })

    file = export_expenses_to_excel(export_data, period_ru)
    filename = f"expenses_{period}_{now.strftime('%Y%m%d')}.xlsx"

    await query.message.delete()
    await query.message.chat.send_document(
        document=file,
        filename=filename,
        caption="📁 Готово! Вот ваш экспорт.",
        reply_markup=get_inline_keyboard("export")
    )


async def export_do(update, context):
    text = update.message.text.strip().lower()
    if text in ["отмена", "❌ отмена"]:
        await update.message.reply_text("Экспорт отменён.", reply_markup=menu_keyboard)
        return ConversationHandler.END

    mapping = {"сегодня": "today", "неделя": "week", "месяц": "month"}
    period = mapping.get(text)
    if not period:
        await update.message.reply_text("Неверный период. Повторите:", reply_markup=cancel_keyboard)
        return EXPORT_PERIOD

    now = datetime.datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - datetime.timedelta(days=7)
    else:
        start = now - datetime.timedelta(days=30)

    session = db_session.create_session()
    expenses = session.query(Expense).options(
        joinedload(Expense.category)
    ).filter(
        Expense.user_id == update.effective_user.id,
        Expense.date >= start
    ).all()
    session.close()

    if not expenses:
        await update.message.reply_text("Нет данных за выбранный период.", reply_markup=menu_keyboard)
        return ConversationHandler.END

    export_data = []
    for e in expenses:
        export_data.append({
            "date": e.date.strftime("%Y-%m-%d"),
            "amount": e.amount,
            "category_name": e.category.name if e.category else "",
            "comment": e.comment or ""
        })

    bio = export_expenses_to_excel(export_data, text)
    filename = f"expenses_{period}_{now.strftime('%Y%m%d')}.xlsx"

    await update.message.reply_document(document=bio, filename=filename, reply_markup=menu_keyboard)
    return ConversationHandler.END


# Регистрация хендлеров
def register_handlers(application):
    application.add_handler(CommandHandler("export", export_start))
    application.add_handler(CallbackQueryHandler(export_button_handler, pattern="^export_"))
