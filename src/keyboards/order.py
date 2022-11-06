from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards import Keyboards
from src.keyboards.callback_patterns import CallbackPatterns
from src.models.const import PaymentType, OrderStatuses, Roles
from src.models.dto import Order


class OrderKeyboards(Keyboards):
    class Reply:
        @classmethod
        def create_order(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                KeyboardButton('Підтвердити ✅'),
                KeyboardButton('Змінити 🔄')
            ]
            return ReplyKeyboardMarkup.from_column(keyboard, resize_keyboard=True)

        @classmethod
        def order_confirm(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton('Доставка 🏍')],
                [KeyboardButton('Заберу самостійно 🚶')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        @classmethod
        def order_proposition_button(cls, value: str = None) -> ReplyKeyboardMarkup:
            return ReplyKeyboardMarkup.from_button(KeyboardButton(value), resize_keyboard=True) if value is not None \
                else Keyboards.remove()

        @classmethod
        def order_payment_type_buttons(cls) -> ReplyKeyboardMarkup:
            keyboard = [KeyboardButton(PaymentType.CARD[1]), KeyboardButton(PaymentType.CASH[1])]
            return ReplyKeyboardMarkup.from_row(keyboard, resize_keyboard=True)

        @classmethod
        def confirm_payment(cls) -> ReplyKeyboardMarkup:
            keyboard = [KeyboardButton('Підтвердити оплату 💳'), KeyboardButton('Скасувати замовлення 🚫')]
            return ReplyKeyboardMarkup.from_column(keyboard)

    class Inline:
        @classmethod
        def order_supplier_actions(cls, order: Order, short_info: bool) -> InlineKeyboardMarkup:
            keyboard = [
                [InlineKeyboardButton(
                    text='Подробнее' if short_info else 'Меньше',
                    callback_data=CallbackPatterns.order_supplier_fl_callback[1].replace('id', str(order.id))
                        .replace('fl', 'full' if short_info else 'less')
                )],
            ]
            status_row = []
            next_status = OrderStatuses.next(order.status, order.payment_type, order.delivery_type, Roles.SUPPLIER)
            if next_status is not None:
                status_row.append(
                    InlineKeyboardButton(
                        text=next_status.label,
                        callback_data=CallbackPatterns.order_supplier_move_state_callback[1].replace('id',
                                                                                                     str(order.id)).replace(
                            'code', str(next_status.code))
                    )
                )
            if len(status_row) > 0:
                keyboard.append(status_row)
            cancel_row = []
            if order.status != OrderStatuses.DECLINED_SUPPLIER.name or not OrderStatuses.get_by_name(
                    order.status).active:
                cancel_row.append(InlineKeyboardButton(
                    text='Отменить заказ',
                    callback_data=CallbackPatterns.order_supplier_cancel_callback[1].replace('id', str(order.id)))
                )
                keyboard.append(cancel_row)

            return InlineKeyboardMarkup(keyboard)

        @classmethod
        def order_supplier_open(cls, order: Order) -> InlineKeyboardMarkup:
            keyboard = [
                # InlineKeyboardButton(
                #     text='Детальнее',
                #     callback_data=CallbackPatterns.order_supplier_open_callback[1].replace('id', str(order.id))
                # )
            ]
            return InlineKeyboardMarkup.from_row(keyboard)

        @classmethod
        def update_escalate_time(cls, order_id, time_str: str):
            return InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(text='Сповістити 💸',
                                     callback_data=
                                     CallbackPatterns.order_notify_confirm[1].replace('id',
                                                                                      order_id).replace(
                                         'time', time_str))
            )

        @classmethod
        def owner_order_cancel(cls, order: Order):
            keyboard = [InlineKeyboardButton(
                text='Скасувати замовлення 🚫',
                callback_data=CallbackPatterns.order_owner_cancel_callback[1].replace('id', str(order.id)))]
            return InlineKeyboardMarkup.from_row(keyboard)
