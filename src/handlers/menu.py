import time
from typing import Dict

from telegram import Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from src.client.positions import PositionClient
from src.handlers import Handlers
from src.handlers.order import OrderHandlers
from src.handlers.states import MENU_CATEGORIES, MAIN_MENU_CUSTOMER
from src.messages.menu import MenuMessages
from src.models.const import Roles
from src.models.dto import Position, Order
from src.utils.cache import Cache

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
            in_order = cls.__in_order(position, tg_user)
            msg, keyboard = MenuMessages.menu_get_position(position, in_order)
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
        if cls.__in_order(position, tg_user):
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
        if not cls.__in_order(position, tg_user):
            _, keyboard = MenuMessages.menu_get_position(position, False)
            try:
                bot.edit_message_reply_markup(tg_user.id, query.message.message_id, reply_markup=keyboard)
            except BadRequest:
                pass
        bot.send_message(tg_user.id, f'Вы убрали <b>{position.name}</b> из своего заказа.', parse_mode=ParseMode.HTML)
        return MENU_CATEGORIES

    @classmethod
    def __in_order(cls, position, tg_user) -> bool:
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        in_order = False
        if order is not None and len(order.positions) > 0:
            for ps in order.positions:
                if ps.id == position.id:
                    in_order = True
                    break
        return in_order
