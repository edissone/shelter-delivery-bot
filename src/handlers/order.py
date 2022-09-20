from typing import Dict, List

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.client.order import OrderClient
from src.client.positions import PositionClient
from src.client.user import UserClient
from src.handlers import Handlers
from src.handlers.states import ORDER_CONFIRM_POSITIONS, MENU_CATEGORIES, ORDER_DELIVERY_PHONE, \
    ORDER_DELIVERY_NAME, ORDER_DELIVERY_ADDRESS, ORDER_PAYMENT_TYPE, ORDER_DELIVERY_NOTES, ORDER_NOTES, \
    ORDER_DELIVERY_TYPE, ORDER_CONFIRM, ORDER_PAYMENT_PAYBACK_FROM, MAIN_MENU_CUSTOMER
from src.keyboards import Keyboards
from src.keyboards.order import OrderKeyboards
from src.messages.menu import MenuMessages
from src.messages.order import OrderMessages
from src.models.const import DeliveryTypes, PaymentType, Roles
from src.models.dto import Order, Position, DeliveryInfo, User
from src.utils.cache import Cache
from src.utils.exceptions import ServiceException, ActiveOrdersExistException
from src.utils.func import compare_time, get_time, in_order
from src.utils.logger import log
from src.utils.validator import Validator

ORDER_TO_SUBMIT = 'order_to_submit'


class OrderHandlers(Handlers):

    # order confirmation
    @classmethod
    def create_order(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)

        if order is None or len(order.positions) < 1:
            err_msg = 'Перед тем, как оформить заказ - выберите желаемые позиции.'
            positions: Dict[str, Dict[int, Position]] = PositionClient.fetch()
            categories = list(positions.keys())
            _, keyboard = MenuMessages.menu_categories(categories)
            bot.send_message(tg_user.id, err_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MENU_CATEGORIES

        msg, keyboard = OrderMessages.create_order(order)
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_CONFIRM_POSITIONS

    @classmethod
    def order_confirm_create(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        operation = update.effective_message.text
        if operation == 'Подтвердить':
            msg, keyboard = OrderMessages.order_confirm_create()
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return ORDER_NOTES
        elif operation == 'Изменить':
            positions: Dict[str, Dict[int, Position]] = PositionClient.fetch()
            categories = list(positions.keys())
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            if order is not None:
                order_positions = list(map(lambda o: Cache.get_positions(id=o.id), order.positions))
                for op in order_positions:
                    is_in_order = in_order(op, tg_user)
                    msg, keyboard = MenuMessages.menu_get_position(op, is_in_order)
                    filename: str = f'resources/images/{op.image}'
                    file = open(filename, 'rb')
                    bot.send_photo(tg_user.id, file, caption=msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            msg, keyboard = MenuMessages.menu_categories(categories)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return MENU_CATEGORIES

    @classmethod
    def order_notes(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        order_notes = update.effective_message.text
        if order_notes != 'Пропустить':
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            order.notes = order_notes
        msg, keyboard = OrderMessages.order_notes()
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_DELIVERY_TYPE

    # order delivery information
    @classmethod
    def order_delivery_type(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        delivery_msg = update.effective_message.text
        user = UserClient.get(tg_user.id)
        delivery_type: str
        if delivery_msg == 'Доставляем':
            delivery_type = DeliveryTypes.DELIVERY
        elif delivery_msg == 'Сами заберем':
            delivery_type = DeliveryTypes.SELF
        else:
            raise RuntimeError('Какая-то хуйня')
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        order.delivery_type = delivery_type
        msg, keyboard = OrderMessages.order_delivery_type(user.full_name,
                                                          'доставку' if delivery_type == DeliveryTypes.DELIVERY else 'cамовывоз')
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_DELIVERY_NAME

    @classmethod
    def order_delivery_name(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        delivery_name = update.effective_message.text
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        order.delivery_info = DeliveryInfo()
        order.delivery_info.full_name = delivery_name
        user = UserClient.get(tg_user.id)
        msg, keyboard = OrderMessages.order_delivery_name(user.phone, order.delivery_type)
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_DELIVERY_PHONE

    @classmethod
    def order_delivery_phone(cls, update: Update, context: CallbackContext) -> int:
        text = update.effective_message.text
        tg_user = update.effective_user
        bot = context.bot
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        if text is None or not Validator.is_phone_number(text):
            err_msg = 'Неверный формат номера. Попробуйте еще раз.'
            user = UserClient.get(tg_user.id)
            _, keyboard = OrderMessages.order_delivery_name(user.phone, order.delivery_type)
            bot.send_message(tg_user.id, err_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return ORDER_DELIVERY_PHONE
        phone = text
        order.delivery_info.phone = phone
        user = UserClient.get(tg_user.id)
        msg, keyboard = OrderMessages.order_delivery_phone(user.address, order.delivery_type)
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_DELIVERY_ADDRESS if order.delivery_type == DeliveryTypes.DELIVERY else ORDER_PAYMENT_TYPE

    @classmethod
    def order_delivery_address(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        user = UserClient.get(tg_user.id)
        delivery_address = update.effective_message.text
        if delivery_address != user.address:
            user.address = delivery_address
            try:
                UserClient.update(user)
            except ServiceException as se:
                log.error(f'USER ADDRESS HAS NOT BEEN UPDATED: {user.tg_id} -> {se.error_message}')
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        order.delivery_info.address = delivery_address
        msg, keyboard = OrderMessages.order_delivery_address()
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_DELIVERY_NOTES

    @classmethod
    def order_delivery_notes(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        delivery_notes = update.effective_message.text
        if delivery_notes == 'Пропустить':
            msg, keyboard = OrderMessages.order_delivery_notes(False)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        else:
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            order.delivery_info.notes = delivery_notes
            msg, keyboard = OrderMessages.order_delivery_notes(True)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_PAYMENT_TYPE

    # order payment information
    @classmethod
    def order_payment_type(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        if message.text in [PaymentType.CARD[1], PaymentType.CASH[1]]:
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            order.payment_type = PaymentType.CARD[0] if message.text == PaymentType.CARD[1] else PaymentType.CASH[0]
            msgs, keyboard = OrderMessages.order_payment_type(order.payment_type, order)
            bot.send_message(tg_user.id, msgs[0], parse_mode=ParseMode.HTML, reply_markup=keyboard)
            if len(msgs) > 1:
                bot.send_message(tg_user.id, msgs[1], parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return ORDER_CONFIRM if order.payment_type == PaymentType.CARD[0] else ORDER_PAYMENT_PAYBACK_FROM

    @classmethod
    def order_payment_payback_from(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        payback_from: float
        try:
            payback_from = float(message.text)
        except ValueError:
            err_msg = 'Неверный формат. Попробуйте еще раз.'
            _, keyboard = OrderMessages.order_payment_type(PaymentType.CASH[0], None)
            bot.send_message(tg_user.id, err_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return ORDER_PAYMENT_PAYBACK_FROM
        cache = Cache.get(tg_user.id)
        order: Order = cache.get(ORDER_TO_SUBMIT)
        if payback_from < order.amount:
            err_msg = f'Сумма для сдачи должна быть больше {order.amount}'
            _, keyboard = OrderMessages.order_payment_type(PaymentType.CASH[0], None)
            bot.send_message(tg_user.id, err_msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return ORDER_PAYMENT_PAYBACK_FROM
        order.payback_from = payback_from
        msgs, keyboard = OrderMessages.order_payment_payback_from(order)
        bot.send_message(tg_user.id, msgs[0], parse_mode=ParseMode.HTML)
        bot.send_message(tg_user.id, msgs[1], parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return ORDER_CONFIRM

    @classmethod
    def order_confirm(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        if message.text == 'Подтвердить':
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            created_order = None
            try:
                created_order = OrderClient.create(order)
            except ActiveOrdersExistException as aoe:
                bot.send_message(tg_user.id, 'Заказ уже создан', parse_mode=ParseMode.HTML,
                                 reply_markup=Keyboards.remove())
                log.error(f'{aoe.error}: {aoe.error_message}')
            if created_order is not None:
                suppliers: List[User] = UserClient.fetch(Roles.SUPPLIER)
                for supp in suppliers:
                    s_msg, s_keyboard = OrderMessages.notify_order_created(created_order)
                    bot.send_message(supp.tg_id, s_msg, parse_mode=ParseMode.HTML, reply_markup=s_keyboard)
                msg = OrderMessages.order_confirm()
                del cache[ORDER_TO_SUBMIT]
                bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=Keyboards.remove())
                return MAIN_MENU_CUSTOMER
            else:
                bot.send_message(tg_user.id, 'Что-то пошло не так =(', parse_mode=ParseMode.HTML,
                                 reply_markup=Keyboards.remove())
                return MAIN_MENU_CUSTOMER

    @classmethod
    def escalate_confirm(cls, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        tg_user = update.effective_user
        message = query.message
        bot = context.bot
        data = query.data.split('_')[1:3]
        order_id = data[0]
        cache = Cache.get(tg_user.id)
        if compare_time(data[1]):
            order = OrderClient.get(int(order_id))

            cache['ESCALATE_MSG'] = message.message_id
            if order is not None:
                query.answer(f'Мы оповестили оператора о вашей оплате', show_alert=True)
                time = get_time(False)
                em_keyboard = OrderKeyboards.Inline.update_escalate_time(order_id, time)
                bot.edit_message_reply_markup(chat_id=tg_user.id, message_id=message.message_id,
                                              reply_markup=em_keyboard)
                bot.send_message(order.supplier_id,
                                 f'{order.delivery_info.full_name} просит проверить оплату заказа номер {order.id}: {order.payment_code}')
        else:
            cache['ESCALATE_MSG'] = message.message_id
            query.answer(f'Мы уже оповестили оператора. Повторно стукнуть можна после {data[1]}', show_alert=True)
        return MAIN_MENU_CUSTOMER
