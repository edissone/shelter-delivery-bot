from typing import List

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards import Keyboards
from src.keyboards.callback_patterns import CallbackPatterns
from src.models.const import Roles, OrderStatuses
from src.models.dto import Order


class MenuKeyboards(Keyboards):
    class Reply:
        @classmethod
        def main_menu(cls, role: str) -> ReplyKeyboardMarkup:
            if role == Roles.CUSTOMER:
                return cls.__main_menu_customer()
            elif role == Roles.SUPPLIER:
                return cls.__main_menu_supplier()
            elif role == Roles.DELIVER:
                return cls.__main_menu_deliver()

        @classmethod
        def __main_menu_customer(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton(text='Меню 🍔')],
                [KeyboardButton(text='Замовлення 📝')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def __main_menu_supplier(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton(text='Просмотреть заказы')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def __main_menu_deliver(cls) -> ReplyKeyboardMarkup:
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
            keyboard.append([KeyboardButton('Головне меню'), KeyboardButton('Замовлення 📝')])
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    class Inline:
        @classmethod
        def menu_get_position(cls, position, in_order) -> InlineKeyboardMarkup:
            keyboard = [
                InlineKeyboardButton(
                    text='Додати у замовлення',
                    callback_data=CallbackPatterns.position_add_pattern[1].replace('id', str(position.id)))
            ]
            if in_order:
                keyboard.append(
                    InlineKeyboardButton(
                        text='Прибрати із замовлення',
                        callback_data=CallbackPatterns.position_remove_pattern[1].replace('id', str(position.id))))
            return InlineKeyboardMarkup.from_row(keyboard)

        @classmethod
        def notify_confirm(cls, order_id: int, time: str) -> InlineKeyboardMarkup:
            keyboard = [InlineKeyboardButton(text='Сповістити 💸',
                                             callback_data=CallbackPatterns.order_notify_confirm[1].replace('id',
                                                                                                            str(order_id)).replace(
                                                 'time', time))]
            return InlineKeyboardMarkup.from_row(keyboard)

        @classmethod
        def delivery_order_actions(cls, order: Order, list_view: bool) -> InlineKeyboardMarkup:
            if list_view:
                return InlineKeyboardMarkup.from_row(
                    [InlineKeyboardButton(
                        text='Взять заказ',
                        callback_data=CallbackPatterns.order_deliver_move_state_callback[1]
                            .replace('id', str(order.id))
                            .replace('code', str(OrderStatuses.ASSIGNED_DEL.code))

                    )]
                )
            else:
                keyboard = []
                status_row = []
                next_status = OrderStatuses.next(order.status, order.payment_type, order.delivery_type, Roles.DELIVER)
                if next_status is not None:
                    status_row.append(
                        InlineKeyboardButton(
                            text=next_status.label,
                            callback_data=CallbackPatterns.order_deliver_move_state_callback[1].replace('id',
                                                                                                         str(order.id)).replace(
                                'code', str(next_status.code))
                        )
                    )
                if len(status_row) > 0:
                    keyboard.append(status_row)
                cancel_row = []
                if order.status != OrderStatuses.DECLINED_DELIVER.name or not OrderStatuses.get_by_name(
                        order.status).active:
                    cancel_row.append(InlineKeyboardButton(
                        text='Отменить заказ',
                        callback_data=CallbackPatterns.order_deliver_cancel_callback[1].replace('id', str(order.id)))
                    )
                    keyboard.append(cancel_row)

                return InlineKeyboardMarkup(keyboard)
