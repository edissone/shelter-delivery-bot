from telegram import ReplyKeyboardMarkup, KeyboardButton

from src.keyboards import Keyboards
from src.models.const import PaymentType


class OrderKeyboards(Keyboards):
    class Reply:
        @classmethod
        def create_order(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                KeyboardButton('Подтвердить'),
                KeyboardButton('Изменить')
            ]
            return ReplyKeyboardMarkup.from_column(keyboard, resize_keyboard=True)

        @classmethod
        def order_confirm(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton('Доставляем')],
                [KeyboardButton('Сами заберем')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def order_proposition_button(cls, value: str = None) -> ReplyKeyboardMarkup:
            return ReplyKeyboardMarkup.from_button(KeyboardButton(value), resize_keyboard=True) if value is not None else Keyboards.remove()

        @classmethod
        def order_payment_type_buttons(cls) -> ReplyKeyboardMarkup:
            keyboard = [KeyboardButton(PaymentType.CARD[1]), KeyboardButton(PaymentType.CASH[1])]
            return ReplyKeyboardMarkup.from_row(keyboard, resize_keyboard=True)
