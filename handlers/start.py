from data import db_session
from data.users import User
from handlers.common import menu_keyboard


async def start(update, context):
    session = db_session.create_session()
    tg_id = update.effective_user.id
    username = update.effective_user.username

    user = session.query(User).get(tg_id)
    if not user:
        user = User(id=tg_id, username=username)
        session.add(user)
        session.commit()
        await update.message.reply_text("Добро пожаловать! Вы зарегистрированы.")
    else:
        await update.message.reply_text("С возвращением!")

    await update.message.reply_text(
        "🧾 <b>Это бот-дневник личных расходов</b>\n"
        "Вы можете добавлять расходы, просматривать статистику и строить графики.\n\n"
        "Используйте меню или команду /help для справки.",
        parse_mode="HTML",
        reply_markup=menu_keyboard
    )
    session.close()
