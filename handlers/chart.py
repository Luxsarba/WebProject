from telegram import InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler
from data import db_session
from utils.plotter import build_pie_chart, build_bar_chart, build_line_chart
from handlers.common import get_chart_keyboard


async def chart_start(update, context):
    context.user_data["chart_type"] = "pie"
    context.user_data["period"] = "week"

    user_id = update.effective_user.id
    session = db_session.create_session()
    buf = build_pie_chart(session, user_id, "week")
    session.close()

    if not buf:
        await update.message.reply_text("Нет данных для построения графика.")
        return

    keyboard = get_chart_keyboard()

    desc = f"Выберите тип графика и период:\n" \
           f"📊 — по категориям\n" \
           f"📅 — по дням\n" \
           f"📈 — накопленные\n\n" \
           f"Периоды: сегодня, неделя, месяц"

    sent = await update.message.reply_photo(photo=buf, caption=desc, reply_markup=keyboard)
    context.user_data["chart_message_id"] = sent.message_id


async def chart_button_handler(update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    message_id = query.message.message_id

    if query.data.startswith("chart_"):
        context.user_data["chart_type"] = query.data.split("_")[1]
    elif query.data.startswith("period_"):
        context.user_data["period"] = query.data.split("_")[1]

    chart_type = context.user_data.get("chart_type", "pie")
    period = context.user_data.get("period", "week")

    session = db_session.create_session()
    if chart_type == "pie":
        buf = build_pie_chart(session, user_id, period)
    elif chart_type == "bar":
        buf = build_bar_chart(session, user_id, period)
    elif chart_type == "line":
        buf = build_line_chart(session, user_id, period)
    else:
        buf = None
    session.close()

    if buf:
        media = InputMediaPhoto(media=buf, caption="График сформирован")
        await query.message.edit_media(media=media)
        await query.message.edit_reply_markup(reply_markup=get_chart_keyboard())
    else:
        await query.message.reply_text("Нет данных для построения графика.")


def register_handlers(application):
    application.add_handler(CommandHandler("chart", chart_start))
    application.add_handler(CallbackQueryHandler(chart_button_handler, pattern="^(chart_|period_).*"))
