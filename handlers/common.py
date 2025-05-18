from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

AMOUNT, CATEGORY, COMMENT = range(3)
PERIOD = range(1)

ADD_AMOUNT, ADD_CATEGORY, ADD_COMMENT = range(3)
SUMMARY_PERIOD = range(1)

EXPORT_PERIOD = range(1)

cancel_keyboard = ReplyKeyboardMarkup(
    [["❌ Отмена"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

menu_keyboard = ReplyKeyboardMarkup([
    ["/add", "/list"],
    ["/summary", "/chart"],
    ["/export", "/help"]
], resize_keyboard=True)

period_names = {
    "today": "сегодня",
    "week": "неделя",
    "month": "месяц"
}


def get_inline_keyboard(prefix: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("сегодня", callback_data=f"{prefix}_today"),
            InlineKeyboardButton("неделя", callback_data=f"{prefix}_week"),
            InlineKeyboardButton("месяц", callback_data=f"{prefix}_month")
        ]
    ])


def get_chart_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊", callback_data="chart_pie"),
            InlineKeyboardButton("📅", callback_data="chart_bar"),
            InlineKeyboardButton("📈", callback_data="chart_line")
        ],
        [
            InlineKeyboardButton("сегодня", callback_data="period_today"),
            InlineKeyboardButton("неделя", callback_data="period_week"),
            InlineKeyboardButton("месяц", callback_data="period_month")
        ]
    ])
