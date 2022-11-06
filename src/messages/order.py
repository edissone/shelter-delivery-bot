from typing import Tuple, Union, List

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup

from src.keyboards import Keyboards
from src.keyboards.order import OrderKeyboards
from src.messages import Messages
from src.models.const import DeliveryTypes, PaymentType
from src.models.dto import Order, Position
from src.utils.cache import Cache


class OrderMessages(Messages):
    @classmethod
    def create_order(cls, order: Order) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/order_confirm_create_info')
        position_list_msg = ''
        amount = 0
        for ps in order.positions:
            position: Position = Cache.get_positions(id=ps.id)
            position_list_msg += f'\n <b><i>{position.name}</i></b>: {ps.count} од., {position.price} грн.\n'
            amount += position.price * ps.count
            order.amount = amount
        msg = msg.replace('$positions$', position_list_msg).replace('$amount$', str(amount))
        return msg, OrderKeyboards.Reply.create_order()

    @classmethod
    def order_notes(cls) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/order_notes')
        keyboard = OrderKeyboards.Reply.order_confirm()
        return msg, keyboard

    @classmethod
    def order_confirm_create(cls) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/order_confirm_create')
        keyboard = OrderKeyboards.Reply.order_proposition_button('Пропустити')
        return msg, keyboard

    @classmethod
    def order_delivery_type(cls, name: str) -> Tuple[
        str, Union[ReplyKeyboardMarkup, ReplyKeyboardRemove]]:
        msg = cls._read_message_text('order/order_delivery_type')
        keyboard = OrderKeyboards.Reply.order_proposition_button(name)
        return msg, keyboard

    @classmethod
    def order_delivery_name(cls, phone: str, delivery_type: str) -> Tuple[
        str, Union[ReplyKeyboardMarkup, ReplyKeyboardRemove]]:
        msg = cls._read_message_text(
            f'order/order_delivery_name{"_del" if delivery_type == DeliveryTypes.DELIVERY else "_self"}')
        keyboard = OrderKeyboards.Reply.order_proposition_button(phone)
        return msg, keyboard

    @classmethod
    def order_delivery_phone(cls, address: str, delivery_type: str) -> Tuple[
        str, Union[ReplyKeyboardMarkup, ReplyKeyboardRemove]]:
        msg = cls._read_message_text(
            f'order/order_delivery_phone{"_del" if delivery_type == DeliveryTypes.DELIVERY else "_self"}')
        keyboard = OrderKeyboards.Reply.order_proposition_button(
            address) if delivery_type == DeliveryTypes.DELIVERY else OrderKeyboards.Reply.order_payment_type_buttons()
        return msg, keyboard

    @classmethod
    def order_delivery_address(cls) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/order_delivery_address')
        keyboard = OrderKeyboards.Reply.order_proposition_button('Пропустити')
        return msg, keyboard

    @classmethod
    def order_delivery_notes(cls, present: bool) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/order_delivery_notes').replace('$notes?$',
                                                                           'Запамʼятали' if present else 'Нічого? Ок)')
        keyboard = OrderKeyboards.Reply.order_payment_type_buttons()
        return msg, keyboard

    @classmethod
    def order_payment_type(cls, payment_type: str, order: Order) -> Tuple[
        List[str], Union[ReplyKeyboardMarkup, ReplyKeyboardRemove]]:
        msgs = [cls._read_message_text(
            f'order/order_payment_type_{"card" if payment_type == PaymentType.CARD[0] else "cash"}')
        ]
        if payment_type == PaymentType.CARD[0]:
            msgs.append(cls._read_message_text('order/order_confirm_info').replace('$order_confirm_info$',
                                                                                   order.info_delivery()))
        keyboard = Keyboards.remove() if payment_type == PaymentType.CASH[0] else OrderKeyboards.Reply.create_order()
        return msgs, keyboard

    @classmethod
    def order_payment_payback_from(cls, order: Order) -> Tuple[List[str], ReplyKeyboardMarkup]:
        msgs = [
            cls._read_message_text('order/order_payment_payback_from'),
            cls._read_message_text('order/order_confirm_info').replace('$order_confirm_info$', order.info_delivery())
        ]
        keyboard = OrderKeyboards.Reply.create_order()
        return msgs, keyboard

    @classmethod
    def order_stub(cls, order: Order, short_info: bool, supplier_name: str = None, delivery_name: str = None):
        msg = order.info() if short_info else order.full_info(supplier_name, delivery_name)
        keyboard = OrderKeyboards.Inline.order_supplier_actions(order, short_info)
        return msg, keyboard

    @classmethod
    def notify_order_created(cls, order: Order) -> Tuple[str, InlineKeyboardMarkup]:
        msg = cls._read_message_text('order/notify_order_created')
        keyboard = OrderKeyboards.Inline.order_supplier_open(order)
        return msg, keyboard

    @classmethod
    def order_confirm(cls) -> str:
        msg = cls._read_message_text('order/order_confirm')
        return msg

    @classmethod
    def confirm_payment(cls, code: str) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('order/confirm_payment').replace('$code$', code)
        keyboard = OrderKeyboards.Reply.confirm_payment()
        return msg, keyboard

    @classmethod
    def owner_order_info(cls, order: Order) -> Tuple[str, InlineKeyboardMarkup]:
        msg = order.owner_info()
        keyboard = OrderKeyboards.Inline.owner_order_cancel(order)
        return msg, keyboard