from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminInlineKeyboard:

    @classmethod
    def home_kb(cls):
        keyboard = [[InlineKeyboardButton(text='🏡 Домой', callback_data='home')]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminMainBlockInline(AdminInlineKeyboard):

    @classmethod
    def main_menu_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="Редактировать монеты", callback_data="edit:coins"),
                InlineKeyboardButton(text="Статистика", callback_data="statistic"),
            ],
            [
                InlineKeyboardButton(text="Заявки", callback_data="tickets"),
                InlineKeyboardButton(text="Рассылка", callback_data="mailing"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminEditionBlockInline(AdminInlineKeyboard):

    @classmethod
    def edition_menu_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="Курсы валют", callback_data="edit:price"),
                InlineKeyboardButton(text="Кошельки", callback_data="edit:wallet"),
            ],
            [InlineKeyboardButton(text="🏡 Домой", callback_data="home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


class AdminTicketsInline(AdminInlineKeyboard):

    @classmethod
    def finish_ticket_kb(cls, user_id: str | int, ticket_id: int):
        keyboard = [
            [
                InlineKeyboardButton(text="📞 Ответить", callback_data=f"connect:{user_id}"),
                InlineKeyboardButton(text="⚓️ Завершить", callback_data=f"finish_ticket:{ticket_id}"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def connect_user_kb(cls, user_id: str | int):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"connect:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
