import datetime
import time
from typing import Dict, List

from telegram import Update, ParseMode, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from src.client.order import OrderClient
from src.client.positions import PositionClient
from src.client.user import UserClient
from src.handlers import Handlers
from src.handlers.order import OrderHandlers
from src.handlers.states import MENU_CATEGORIES, MAIN_MENU_CUSTOMER, MAIN_MENU_SUPPLIER
from src.messages.menu import MenuMessages
from src.messages.order import OrderMessages
from src.models.const import Roles, OrderStatuses, PaymentType
from src.models.dto import Position, Order
from src.utils.cache import Cache
from src.utils.exceptions import NotFoundException
from src.utils.func import get_time, in_order
from src.utils.logger import log

ORDER_TO_SUBMIT = 'order_to_submit'


class MenuHandlers(Handlers):
    @classmethod
    def main_menu_customer(cls, update: Update, context: CallbackContext) -> int:
        message = update.effective_message
        bot = context.bot
        if message.text == 'Меню':
            return cls.__menu_categories(update, context)
        elif message.text == 'Оформить заказ':
            return OrderHandlers.create_order(update, context)

    @classmethod
    def __menu_categories(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        positions: Dict[str, Dict[int, Position]] = PositionClient.fetch()
        categories = list(positions.keys())
        msg, keyboard = MenuMessages.menu_categories(categories)
        bot.send_message(tg_user.id, msg, reply_markup=keyboard)
        return MENU_CATEGORIES

    @classmethod
    def menu_get_positions(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        operation = message.text
        if operation == 'Главное меню':
            msg, keyboard = MenuMessages.main_menu(Roles.CUSTOMER)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MAIN_MENU_CUSTOMER
        if operation == 'Оформить заказ':
            return OrderHandlers.create_order(update, context)
        positions = Cache.get_positions(operation)
        if positions is None:
            err_msg = 'Такой категории нет :(.'
            bot.send_message(tg_user.id, err_msg)
            return MENU_CATEGORIES
        for position in positions.values():
            is_in_order = in_order(position, tg_user)
            msg, keyboard = MenuMessages.menu_get_position(position, is_in_order)
            filename: str = f'resources/images/{position.image}'
            file = open(filename, 'rb')
            bot.send_photo(tg_user.id, file, caption=msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            time.sleep(1)
        return MENU_CATEGORIES

    @classmethod
    def add_position(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        position_id = query.data.split('_')[1]
        position = Cache.get_positions(id=int(position_id))
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        if order is None:
            cache[ORDER_TO_SUBMIT] = Order(owner_id=tg_user.id, positions=[])
            order = cache[ORDER_TO_SUBMIT]
        order.add_position_stub(position)
        query.answer()
        if in_order(position, tg_user):
            _, keyboard = MenuMessages.menu_get_position(position, True)
            try:
                bot.edit_message_reply_markup(tg_user.id, query.message.message_id, reply_markup=keyboard)
            except BadRequest:
                pass
        bot.send_message(tg_user.id, f'Вы добавили <b>{position.name}</b> в свой заказ.', parse_mode=ParseMode.HTML)
        return MENU_CATEGORIES

    @classmethod
    def remove_position(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        position_id = query.data.split('_')[1]
        position = Cache.get_positions(id=int(position_id))
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        if order is None:
            bot.send_message(tg_user.id, f'Нельзя убрать не добавив!',
                             parse_mode=ParseMode.HTML)
            return MENU_CATEGORIES
        order.remove_position_stub(position)
        query.answer()
        if not in_order(position, tg_user):
            _, keyboard = MenuMessages.menu_get_position(position, False)
            try:
                bot.edit_message_reply_markup(tg_user.id, query.message.message_id, reply_markup=keyboard)
            except BadRequest:
                pass
        bot.send_message(tg_user.id, f'Вы убрали <b>{position.name}</b> из своего заказа.', parse_mode=ParseMode.HTML)
        return MENU_CATEGORIES

    @classmethod
    def main_menu_supplier(cls, update: Update, context: CallbackContext) -> int:
        message = update.effective_message
        bot = context.bot
        if message.text == 'Просмотреть заказы':
            return cls.order_list(update, context)

    @classmethod
    def order_list(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        orders: List[Order] = OrderClient.fetch(active=True)
        if len(orders) > 0:
            for order in orders:
                msg, keyboard = OrderMessages.order_stub(order, False)
                bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MAIN_MENU_SUPPLIER
        else:
            bot.send_message(tg_user.id, 'Заказов нет', parse_mode=ParseMode.HTML)
            return MAIN_MENU_SUPPLIER

    @classmethod
    def supplier_fl_order_info(cls, update: Update, context: CallbackContext) -> int:
        callback = update.callback_query.data.split("_")[1:3]
        tg_user = update.effective_user
        order_id = int(callback[0])
        short: bool = callback[1] == 'less'
        bot = context.bot
        query = update.callback_query
        message = query.message
        order = OrderClient.get(order_id)
        supplier = get_optional_user(order.supplier_id) if not short else None
        deliver = get_optional_user(order.delivery_id) if not short else None
        msg, keyboard = OrderMessages.order_stub(
            order, short,
            supplier_name=supplier.full_name if supplier is not None else None,
            delivery_name=deliver.full_name if deliver is not None else None
        )
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=msg,
            parse_mode=ParseMode.HTML
        )
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=keyboard)
        query.answer()
        return MAIN_MENU_SUPPLIER

    @classmethod
    def supplier_cancel_callback(cls, update: Update, context: CallbackContext) -> int:
        order_id = int(update.callback_query.data.split("_")[1])
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        message = query.message
        order: Order = OrderClient.decline(order_id, tg_user.id)
        if order is not None:
            query.answer()
            bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                          reply_markup=InlineKeyboardMarkup.from_row([]))
            bot.edit_message_text(
                message_id=message.message_id, chat_id=tg_user.id,
                text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
                parse_mode=ParseMode.HTML
            )
            bot.send_message(
                order.owner_id,
                'Ваш заказ отменен оператором',
                parse_mode=ParseMode.HTML
            )
        return MAIN_MENU_SUPPLIER

    @classmethod
    def supplier_move_to_state_callback(cls, update: Update, context: CallbackContext) -> int:
        callback = update.callback_query.data.split("_")[1:3]
        bot = context.bot
        order_id = int(callback[0])
        status_code = int(callback[1])
        status_handler = SUPPLIER_STATUS_HANDLERS.get(status_code)
        if status_handler is not None:
            return status_handler(update, context, order_id)
        else:
            bot.send_message(update.effective_user.id, 'Что-то пошло не так =(', parse_mode=ParseMode.HTML)
        return MAIN_MENU_SUPPLIER


def get_optional_user(id: str):
    try:
        return UserClient.get(id)
    except NotFoundException as nf:
        log.info(f'{nf.error}: {nf.error_message}')
        return None


def assign_supplier(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.assign(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = OrderMessages.order_stub(order, True)
        bot.send_message(order.supplier_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.owner_id,
            f'Ваш заказ в обработке{" и уже готовится" if OrderStatuses.get_by_name(order.status) == OrderStatuses.PREPARING else " =)"}',
            parse_mode=ParseMode.HTML
        )
        if order.payment_type == PaymentType.CARD[0]:
            str_time = get_time(True)
            cc_msg, cc_keyboard = MenuMessages.notify_confirm(order.payment_code, order_id, str_time,
                                                              '0000 0000 0000 0000')
            bot.send_message(
                order.owner_id,
                text=cc_msg,
                reply_markup=cc_keyboard,
                parse_mode=ParseMode.HTML
            )
        return MAIN_MENU_SUPPLIER


def confirm_supplier(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.confirm(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = OrderMessages.order_stub(order, True)
        bot.send_message(order.supplier_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.owner_id,
            f'Оплата подтверждена оператором. Готовим ваш заказ =)',
            parse_mode=ParseMode.HTML
        )
        cache = Cache.get(int(order.owner_id))
        m_id = cache.get('ESCALATE_MSG')
        if m_id is not None:
            bot.delete_message(chat_id=order.owner_id, message_id=m_id)
    return MAIN_MENU_SUPPLIER


def ready_del_supplier(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.ready(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = OrderMessages.order_stub(order, True)
        bot.send_message(order.supplier_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.owner_id,
            f'Заказ готов, ждем пока наш доставщик его заберет =)',
            parse_mode=ParseMode.HTML
        )
    return MAIN_MENU_SUPPLIER


def ready_self_supplier(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.ready(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = OrderMessages.order_stub(order, True)
        bot.send_message(order.supplier_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.owner_id,
            f'Заказ готов, можете забирать =)',
            parse_mode=ParseMode.HTML
        )
    return MAIN_MENU_SUPPLIER


def got_self_supplier(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.got_self(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>, ЗАКРЫТ',
            parse_mode=ParseMode.HTML
        )
        bot.send_message(
            order.owner_id,
            text=f'Спасибо за заказ =)',
            parse_mode=ParseMode.HTML
        )
    return MAIN_MENU_SUPPLIER


SUPPLIER_STATUS_HANDLERS = {
    OrderStatuses.ASSIGNED.code: assign_supplier,
    OrderStatuses.CONFIRM.code: confirm_supplier,
    OrderStatuses.READY_DEL.code: ready_del_supplier,
    OrderStatuses.READY_SELF.code: ready_self_supplier,
    OrderStatuses.GOT_SELF.code: got_self_supplier
}
