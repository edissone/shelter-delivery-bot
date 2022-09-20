from typing import List

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards import Keyboards
from src.keyboards.callback_patterns import CallbackPatterns
from src.models.const import Roles


class MenuKeyboards(Keyboards):
    class Reply:
        @classmethod
        def main_menu(cls, role: str) -> ReplyKeyboardMarkup:
            if role == Roles.CUSTOMER:
                return cls.__main_menu_customer()
            elif role == Roles.SUPPLIER:
                return cls.__main_menu_supplier()

        @classmethod
        def __main_menu_customer(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton(text='Меню')],
                [KeyboardButton(text='Оформить заказ')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def __main_menu_supplier(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton(text='Просмотреть заказы')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def menu_categories(cls, categories: List[str]):
            keyboard = []
            i = 0
            while i < len(categories):
                cell = [KeyboardButton(categories[i])]
                if len(categories) - i > 1:
                    i += 1
                    cell.append(KeyboardButton(categories[i]))
                keyboard.append(cell)
                i += 1
            keyboard.append([KeyboardButton('Главное меню'), KeyboardButton('Оформить заказ')])
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    class Inline:
        @classmethod
        def menu_get_position(cls, position, in_order) -> InlineKeyboardMarkup:
            keyboard = [
                InlineKeyboardButton(
                    text='Добавить в заказ',
                    callback_data=CallbackPatterns.position_add_pattern[1].replace('id', str(position.id)))
            ]
            if in_order:
                keyboard.append(
                    InlineKeyboardButton(
                        text='Убрать из заказа',
                        callback_data=CallbackPatterns.position_remove_pattern[1].replace('id', str(position.id))))
            return InlineKeyboardMarkup.from_row(keyboard)

        @classmethod
        def notify_confirm(cls, order_id: int, time: str) -> InlineKeyboardMarkup:
            keyboard = [InlineKeyboardButton(text='Оповестить',
                                             callback_data=CallbackPatterns.order_notify_confirm[1].replace('id',
                                                                                                            str(order_id)).replace(
                                                 'time', time))]
            return InlineKeyboardMarkup.from_row(keyboard)
