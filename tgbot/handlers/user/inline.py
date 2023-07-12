from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class UserInlineKeyboard:

    @classmethod
    def home_kb(cls):
        keyboard = [[InlineKeyboardButton(text='🏡 Домой', callback_data='home')]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard


class UserMainBlockInline(UserInlineKeyboard):

    @classmethod
    def main_menu_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="💷 продать крипту", callback_data="operation:sell"),
                InlineKeyboardButton(text="❔ Посмотреть курс", callback_data="get_course"),
            ],
            [
                InlineKeyboardButton(text="📱 Наш канал", url="https://t.me/minerworldex"),
                InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"),
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard


class UserSellCryptoInline(UserInlineKeyboard):

    @classmethod
    def edition_menu_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="Курсы валют", callback_data="edit:price"),
                InlineKeyboardButton(text="Кошельки", callback_data="edit:wallet"),
            ],
            [InlineKeyboardButton(text="🏡 Домой", callback_data="home")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def sell_coins_kb(cls, coins: list):
        keyboard = []
        for coin in coins:
            coin_title = coin["title"]
            keyboard.append([InlineKeyboardButton(text=coin_title, callback_data=f"sell:{coin_title}")])
        keyboard.append([InlineKeyboardButton(text="🏡 Домой", callback_data="home")])
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def sell_accept_kb(cls):
        keyboard = [
            [
                InlineKeyboardButton(text="👍 Подтвердить", callback_data="sell_accept"),
                InlineKeyboardButton(text="👎 Отменить", callback_data="home"),
            ],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)
        return keyboard

    @classmethod
    def connect_user_kb(cls, user_id: str | int):
        keyboard = [[InlineKeyboardButton(text="📞 Ответить", callback_data=f"connect:{user_id}")]]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @classmethod
    def finish_ticket_kb(cls, user_id: str | int, ticket_id: int):
        keyboard = [
            [
                InlineKeyboardButton(text="📞 Ответить", callback_data=f"connect:{user_id}"),
                InlineKeyboardButton(text="⚓️ Завершить", callback_data=f"finish_ticket:{ticket_id}"),
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
