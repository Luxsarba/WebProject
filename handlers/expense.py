from telegram.ext import (ConversationHandler,
                          MessageHandler, CommandHandler,
                          CallbackQueryHandler, filters)
import sqlalchemy as sa
import datetime
from data import db_session
from data.expenses import Expense
from data.categories import Category
from handlers.start import menu_keyboard
from handlers.common import (AMOUNT, CATEGORY, COMMENT, PERIOD,
                             cancel_keyboard, period_names,
                             get_inline_keyboard)


# /add
async def add_expense_start(update, context):
    await update.message.reply_text("Введите сумму расхода:", reply_markup=cancel_keyboard)
    return AMOUNT


async def add_expense_amount(update, context):
    if update.message.text.lower() in ["отмена", "❌ отмена"]:
        return await add_expense_cancel(update, context)
    try:
        amount = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом. Повторите:")
        return AMOUNT

    context.user_data["amount"] = amount
    await update.message.reply_text("Введите категорию (например, еда, такси):", reply_markup=cancel_keyboard)
    return CATEGORY


async def add_expense_category(update, context):
    if update.message.text.lower() in ["отмена", "❌ отмена"]:
        return await add_expense_cancel(update, context)
    context.user_data["category"] = update.message.text.strip()
    await update.message.reply_text("Добавьте комментарий или напишите «-», если не нужен:",
                                    reply_markup=cancel_keyboard)
    return COMMENT


async def add_expense_comment(update, context):
    if update.message.text.lower() in ["отмена", "❌ отмена"]:
        return await add_expense_cancel(update, context)
    comment = update.message.text.strip()
    user_id = update.effective_user.id
    session = db_session.create_session()

    category_name = context.user_data["category"]
    category = session.query(Category).filter_by(name=category_name, user_id=user_id).first()
    if not category:
        category = Category(name=category_name, user_id=user_id)
        session.add(category)
        session.commit()

    expense = Expense(
        user_id=user_id,
        amount=context.user_data["amount"],
        category_id=category.id,
        comment=None if comment == "-" else comment
    )
    session.add(expense)
    session.commit()
    session.close()

    await update.message.reply_text("✅ Расход добавлен!", reply_markup=menu_keyboard)
    return ConversationHandler.END


async def add_expense_cancel(update, context):
    await update.message.reply_text("Операция отменена.", reply_markup=menu_keyboard)
    return ConversationHandler.END


# /list
async def list_expenses(update, context):
    session = db_session.create_session()
    user_id = update.effective_user.id
    expenses = (
        session.query(Expense)
        .filter_by(user_id=user_id)
        .order_by(Expense.date.desc())
        .limit(10)
        .all()
    )
    if not expenses:
        await update.message.reply_text("У вас пока нет расходов.", reply_markup=menu_keyboard)
        return

    lines = []
    for e in expenses:
        date = e.date.strftime("%d.%m.%Y")
        cat = e.category.name if e.category else "без категории"
        comment = f" ({e.comment})" if e.comment else ""
        lines.append(f"{date}: {e.amount}₽ — {cat}{comment}")

    await update.message.reply_text("\n".join(lines), reply_markup=menu_keyboard)
    session.close()


# /summary
async def summary_start(update, context):
    keyboard = get_inline_keyboard("summary")
    await update.message.reply_text("Выберите период для просмотра суммы расходов:", reply_markup=keyboard)


async def summary_button_handler(update, context):
    query = update.callback_query
    await query.answer()
    period = query.data.split("_")[1]

    user_id = query.from_user.id
    now = datetime.datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - datetime.timedelta(days=7)
    else:
        start = now - datetime.timedelta(days=30)

    session = db_session.create_session()
    total = (
                session.query(Expense)
                .filter(Expense.user_id == user_id, Expense.date >= start)
                .with_entities(sa.func.sum(Expense.amount))
                .scalar()
            ) or 0
    session.close()

    await query.message.edit_text(
        f"💰 Сумма расходов за {period_names[period]}: {round(total, 2)} ₽",
        reply_markup=get_inline_keyboard("summary")
    )


async def summary_show(update, context):
    if update.message.text.lower() in ["отмена", "❌ отмена"]:
        return await summary_cancel(update, context)

    period_input = update.message.text.strip().lower()
    mapping = {"сегодня": "today", "неделя": "week", "месяц": "month"}
    period = mapping.get(period_input)

    if not period:
        await update.message.reply_text("Некорректный период. Попробуйте ещё раз:")
        return PERIOD

    user_id = update.effective_user.id
    now = datetime.datetime.now()

    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - datetime.timedelta(days=7)
    elif period == "month":
        start_date = now - datetime.timedelta(days=30)

    session = db_session.create_session()
    total = (
                session.query(sa.func.sum(Expense.amount))
                .filter(Expense.user_id == user_id, Expense.date >= start_date)
                .scalar()
            ) or 0
    session.close()

    await update.message.reply_text(f"Сумма расходов за {period_input}: {round(total, 2)}₽", reply_markup=menu_keyboard)
    return ConversationHandler.END


async def summary_cancel(update, context):
    await update.message.reply_text("Операция отменена.", reply_markup=menu_keyboard)
    return ConversationHandler.END


# Регистрация хендлеров

def register_handlers(application):
    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_expense_start)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_amount)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_category)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_expense_comment)],
        },
        fallbacks=[MessageHandler(filters.Regex("(?i)^❌ отмена$"), add_expense_cancel)],
        allow_reentry=True
    )
    application.add_handler(add_conv)

    application.add_handler(CommandHandler("summary", summary_start))
    application.add_handler(CallbackQueryHandler(summary_button_handler, pattern="^summary_"))
    application.add_handler(CommandHandler("list", list_expenses))
