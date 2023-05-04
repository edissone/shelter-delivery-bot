import time
from typing import Dict, List, Optional

from telegram import Update, ParseMode, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from src.client.order import OrderClient
from src.client.positions import PositionClient
from src.client.report import ReportClient
from src.client.user import UserClient
from src.handlers import Handlers
from src.handlers.order import OrderHandlers
from src.handlers.states import MENU_CATEGORIES, MAIN_MENU_CUSTOMER, MAIN_MENU_SUPPLIER, MAIN_MENU_DELIVER, \
    REPORT_OPTION, SUPPLIER_ADD_DELIVER, SUPPLIER_REMOVE_DELIVER
from src.keyboards import Keyboards
from src.keyboards.menu import MenuKeyboards
from src.messages.menu import MenuMessages
from src.messages.order import OrderMessages
from src.messages.report import ReportMessages
from src.models.const import Roles, OrderStatuses, PaymentType, resource_params, ReportOptions
from src.models.dto import Position, Order, User
from src.utils.cache import Cache
from src.utils.exceptions import NotFoundException, InvalidStateException, AlreadyExists
from src.utils.func import get_time, in_order
from src.utils.giphy import gif
from src.utils.logger import log
from src.utils.report import ReportBuilder
from src.utils.timer import in_time

ORDER_TO_SUBMIT = 'order_to_submit'


class MenuHandlers(Handlers):
    @classmethod
    def main_menu_customer(cls, update: Update, context: CallbackContext) -> int:
        message = update.effective_message
        bot = context.bot
        if message.text == 'Меню 🍔':
            return cls.__menu_categories(update, context)
        elif message.text == 'Замовлення 📝':
            return OrderHandlers.create_order(update, context)
        elif message.text == 'Допомога ℹ️':
            return cls.help(update, context)

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
        if operation == 'Головне меню':
            msg, keyboard = MenuMessages.main_menu(Roles.CUSTOMER)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MAIN_MENU_CUSTOMER
        if operation == 'Замовлення 📝':
            return OrderHandlers.create_order(update, context)
        positions = Cache.get_positions(operation)
        owner_orders: List[Order] = OrderClient.get_by_owner(tg_user.id)
        active = list(filter(lambda o: OrderStatuses.get_by_name(o.status) in OrderStatuses.active(), owner_orders))
        if positions is None:
            err_msg = 'Цієї категорії немає :(.'
            bot.send_message(tg_user.id, err_msg)
            return MENU_CATEGORIES
        for position in positions.values():
            is_in_order = in_order(position, tg_user)
            msg, keyboard = MenuMessages.menu_get_position(position, is_in_order)
            if position.image is not None:
                filename: str = f'resources/images/{position.image}'
                file = open(filename, 'rb')
                bot.send_photo(tg_user.id, file, caption=msg, parse_mode=ParseMode.HTML,
                               reply_markup=None if len(active) != 0 or not in_time() else keyboard)
            else:
                bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            time.sleep(1)
        return MENU_CATEGORIES

    @classmethod
    def add_position(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        owner_orders: List[Order] = OrderClient.get_by_owner(tg_user.id)
        active = list(filter(lambda o: OrderStatuses.get_by_name(o.status) in OrderStatuses.active(), owner_orders))
        if len(active) == 0:
            position_id = query.data.split('_')[1]
            position = Cache.get_positions(id=int(position_id))
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            if order is None:
                cache[ORDER_TO_SUBMIT] = Order(owner_id=tg_user.id, positions=[])
                order = cache[ORDER_TO_SUBMIT]
            order.add_position_stub(position)
            if in_order(position, tg_user):
                _, keyboard = MenuMessages.menu_get_position(position, True)
                try:
                    bot.edit_message_reply_markup(tg_user.id, query.message.message_id, reply_markup=keyboard)
                except BadRequest:
                    pass
            msg = f'Ви додали <b>{position.name}</b> у своє замовлення 🍽'
            query.answer(f'Ви додали {position.name} у своє замовлення 🍽', show_alert=True)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML)
        else:
            query.answer(text='Ви вже маєте активне замовлення.', show_alert=True)
        return MENU_CATEGORIES

    @classmethod
    def remove_position(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        owner_orders: List[Order] = OrderClient.get_by_owner(tg_user.id)
        active = list(filter(lambda o: OrderStatuses.get_by_name(o.status) in OrderStatuses.active(), owner_orders))
        if len(active) == 0:
            position_id = query.data.split('_')[1]
            position = Cache.get_positions(id=int(position_id))
            cache = Cache.get(tg_user.id)
            order: Order = cache.get(ORDER_TO_SUBMIT)
            if order is None:
                bot.send_message(tg_user.id, f'Не можна видаляти, не додавши!',
                                 parse_mode=ParseMode.HTML)
                return MENU_CATEGORIES
            order.remove_position_stub(position)
            if not in_order(position, tg_user):
                _, keyboard = MenuMessages.menu_get_position(position, False)
                try:
                    bot.edit_message_reply_markup(tg_user.id, query.message.message_id, reply_markup=keyboard)
                except BadRequest:
                    pass
            query.answer(f'Ви прибрали {position.name} зі свого замовлення 🍽')
            msg = f'Ви прибрали <b>{position.name}</b> зі свого замовлення 🍽'
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML)
        else:
            query.answer(text='Ви вже маєте активне замовлення.', show_alert=True)
        return MENU_CATEGORIES

    # Supplier

    @classmethod
    def main_menu_supplier(cls, update: Update, context: CallbackContext) -> int:
        message = update.effective_message
        bot = context.bot
        if message.text == 'Просмотреть заказы':
            return cls.order_list(update, context)
        elif message.text == 'Получить отчет':
            return cls.report(update, context)
        elif message.text == 'Добавить курьера':
            return cls.supplier_add_deliver(update, context)
        elif message.text == 'Удалить курьера':
            return cls.supplier_remove_deliver(update, context)

    @classmethod
    def supplier_add_deliver(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        bot.send_message(tg_user.id, 'Необходимо отправить telegram-контакт куръера', reply_markup=Keyboards.remove())
        return SUPPLIER_ADD_DELIVER

    @classmethod
    def supplier_add_deliver_handle_contact(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        contact = message.contact
        if contact.user_id is None:
            bot.send_message(tg_user.id, 'Неверный формат. Необходим контакт учетной записи telegram',
                             reply_markup=MenuMessages.main_menu(Roles.SUPPLIER)[1])
            return MAIN_MENU_SUPPLIER
        try:
            UserClient.add_deliver(User(tg_id=str(contact.user_id), phone=contact.phone_number,
                                        full_name=contact.first_name,
                                        role=Roles.DELIVER))
        except AlreadyExists as ae:
            bot.send_message(tg_user.id, 'Пользователь уже создан', reply_markup=MenuMessages.main_menu(Roles.SUPPLIER)[1])
            log.exception(ae.error_message)
            return MAIN_MENU_SUPPLIER
        bot.send_message(tg_user.id, 'Пользователь создан', reply_markup=MenuMessages.main_menu(Roles.SUPPLIER)[1])
        return MAIN_MENU_SUPPLIER

    @classmethod
    def supplier_remove_deliver(cls, update: Update, context: CallbackContext):
        tg_user = update.effective_user
        bot = context.bot
        delivers = UserClient.fetch(Roles.DELIVER)
        state = -1
        if delivers is None:
            msg = 'Курьеров нет'
            state = MAIN_MENU_SUPPLIER
            bot.send_message(tg_user.id, msg, reply_markup=MenuMessages.main_menu(Roles.SUPPLIER)[1])
        else:
            msg = 'Выберите имя курьера для удаления'
            keyboard = MenuKeyboards.Inline.user_list(delivers)
            state = SUPPLIER_REMOVE_DELIVER
            bot.send_message(tg_user.id, msg, reply_markup=keyboard)
        return state

    @classmethod
    def supplier_remove_deliver_handle_name(cls, update: Update, context: CallbackContext):
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        deletable_id = query.data.split("_")[1]
        try:
            user = UserClient.remove_user_role(deletable_id)
            msg = f'Успешно удален {user.full_name}'
        except NotFoundException as nfe:
            log.exception(nfe.error_message)
            msg = 'Пользователь не найден'
        query.answer()
        bot.send_message(tg_user.id, msg, reply_markup=MenuMessages.main_menu(Roles.SUPPLIER)[1])
        query.delete_message()
        return MAIN_MENU_SUPPLIER

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
    def report(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        msg, keyboard = ReportMessages.report_option()
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return REPORT_OPTION

    @classmethod
    def report_get_report(cls, update: Update, context: CallbackContext):
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        option = ReportOptions.get(int(query.data.split('_')[1]))
        report = ReportBuilder.build_report(ReportClient.get_report(option[0]))
        query.delete_message()
        query.answer()
        bot.send_document(tg_user.id, report)
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
                'Ваше замовлення скасовано оператором 👨🏻‍💻',
                parse_mode=ParseMode.HTML
            )
            if order.delivery_id is not None:
                bot.send_message(
                    order.delivery_id,
                    f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
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

    # Deliver

    @classmethod
    def main_menu_delivery(cls, update: Update, context: CallbackContext) -> int:
        message = update.effective_message
        bot = context.bot
        if message.text == 'Просмотреть заказы':
            return cls.order_list_deliver(update, context)

    @classmethod
    def order_list_deliver(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        orders: List[Order] = OrderClient.fetch(status=OrderStatuses.READY_DEL.name)
        assigned_order: Optional[Order] = None
        try:
            assigned_order = OrderClient.fetch_assigned(tg_user.id, True)
        except NotFoundException as nfe:
            log.info(f'{nfe.error}:{nfe.error_message}')
        empty: bool = True
        if len(orders) > 0 and assigned_order is None:
            for order in orders:
                if order.delivery_id is None or order.delivery_id == '':
                    msg, keyboard = MenuMessages.delivery_order_stub(order, True)
                    bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
                    empty = False
        elif assigned_order is not None:
            msg, keyboard = MenuMessages.delivery_order_stub(assigned_order, False)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MAIN_MENU_DELIVER
        if empty:
            bot.send_message(tg_user.id, 'Заказов нет', parse_mode=ParseMode.HTML)
        return MAIN_MENU_DELIVER

    @classmethod
    def deliver_cancel_callback(cls, update: Update, context: CallbackContext) -> int:
        order_id = int(update.callback_query.data.split("_")[1])
        tg_user = update.effective_user
        bot = context.bot
        query = update.callback_query
        message = query.message
        try:
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
                    order.supplier_id,
                    f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>'
                    f' by доставщик',
                    parse_mode=ParseMode.HTML
                )
                bot.send_message(
                    order.owner_id,
                    'Ваше замовлення скасовано курʼєром 🏍',
                    parse_mode=ParseMode.HTML
                )
        except InvalidStateException as ise:
            log.info('{}, {}', ise.error, ise.error_message)
        return MAIN_MENU_DELIVER

    @classmethod
    def deliver_move_to_state_callback(cls, update: Update, context: CallbackContext) -> int:
        callback = update.callback_query.data.split("_")[1:3]
        bot = context.bot
        order_id = int(callback[0])
        status_code = int(callback[1])
        status_handler = DELIVER_STATUS_HANDLERS.get(status_code)
        if status_handler is not None:
            return status_handler(update, context, order_id)
        else:
            bot.send_message(update.effective_user.id, 'Щось не так =(', parse_mode=ParseMode.HTML)
        return MAIN_MENU_DELIVER


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
        cc_msg = f'Ваше замовлення в обробці{" і вже готується 👨🏾‍🍳 🍔" if OrderStatuses.get_by_name(order.status) == OrderStatuses.PREPARING else " 📝"}'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
        )
        if order.payment_type == PaymentType.CARD[0]:
            str_time = get_time(True)
            cc_msg, cc_keyboard = MenuMessages.notify_confirm(order.payment_code, order_id, str_time,
                                                              resource_params['pay_card'])
            bot.send_animation(
                chat_id=order.owner_id,
                animation=gif(order.status),
                caption=cc_msg,
                reply_markup=cc_keyboard,
                parse_mode=ParseMode.HTML,
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
        cc_msg = f'Оплата підтверджена. Готуємо ваше замовлення 👨🏾‍🍳 🍔'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
            parse_mode=ParseMode.HTML,
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
        cc_msg = f'Ура! Замовлення готове. Зараз кур‘єр забере замовлення і скоро буде у вас 🖤'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
            parse_mode=ParseMode.HTML,
        )
        s_msg, s_keyboard = OrderMessages.notify_order_created(order)
        delivers: List[User] = UserClient.fetch(Roles.DELIVER)
        for deliver in delivers:
            s_msg, s_keyboard = OrderMessages.notify_order_created(order)
            bot.send_message(deliver.tg_id, s_msg, parse_mode=ParseMode.HTML, reply_markup=s_keyboard)
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
        cc_msg = f'Ура! Замовлення вже очікує на вас =)'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
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
        cc_msg = f'Отримали? Приємного смаку і до зустрічі 😏'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
        )
    return MAIN_MENU_SUPPLIER


SUPPLIER_STATUS_HANDLERS = {
    OrderStatuses.ASSIGNED.code: assign_supplier,
    OrderStatuses.CONFIRM.code: confirm_supplier,
    OrderStatuses.READY_DEL.code: ready_del_supplier,
    OrderStatuses.READY_SELF.code: ready_self_supplier,
    OrderStatuses.GOT_SELF.code: got_self_supplier
}


def assign_delivery(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    assigned_order: Order = None
    try:
        assigned_order = OrderClient.fetch_assigned(tg_user.id, True)
    except NotFoundException as nfe:
        log.info(f'{nfe.error}:{nfe.error_message}')
    order: Order = OrderClient.assign(order_id, tg_user.id)
    if order is not None and assigned_order is None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = MenuMessages.delivery_order_stub(order, False)
        bot.send_message(order.delivery_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        del_user: Optional[User] = None
        try:
            del_user = UserClient.get(tg_user.id)
        except NotFoundException as nfe:
            log.error(f'{nfe.error}:{nfe.error_message}')
        bot.send_message(
            order.supplier_id,
            f'Заказ с номером {order_id} перешел в состояние <i>'
            f'{OrderStatuses.get_by_name(order.status).label}</i>, '
            f'by {del_user.full_name if del_user is not None else "Имя неизвестно"}',
            parse_mode=ParseMode.HTML
        )
        return MAIN_MENU_DELIVER
    elif assigned_order is not None:
        bot.send_message(tg_user.id, 'Вы не можете взять новый заказ, пока работаете на другим',
                         parse_mode=ParseMode.HTML)
        return MAIN_MENU_DELIVER


def going_delivery(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.going(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = MenuMessages.delivery_order_stub(order, False)
        bot.send_message(order.delivery_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.supplier_id,
            f'Заказ с номером {order_id} перешел в состояние <i>'
            f'{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        cc_msg = f'Курʼєр вже отримав ваше замовелння. Незабаром воно буде у вас 🕒'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
            parse_mode=ParseMode.HTML,
        )
        return MAIN_MENU_DELIVER


def arrived_delivery(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.arrived(order_id, tg_user.id)
    if order is not None:
        query.answer()
        bot.edit_message_reply_markup(message_id=message.message_id, chat_id=tg_user.id,
                                      reply_markup=InlineKeyboardMarkup([[]]))
        bot.edit_message_text(
            message_id=message.message_id, chat_id=tg_user.id,
            text=f'Заказ с номером {order_id} перешел в состояние <i>{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        msg, keyboard = MenuMessages.delivery_order_stub(order, False)
        bot.send_message(order.delivery_id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        bot.send_message(
            order.supplier_id,
            f'Заказ с номером {order_id} перешел в состояние <i>'
            f'{OrderStatuses.get_by_name(order.status).label}</i>',
            parse_mode=ParseMode.HTML
        )
        cc_msg = f'Курʼєр вже чекає на вас!'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
            parse_mode=ParseMode.HTML,
        )
        return MAIN_MENU_DELIVER


def delivered_delivery(update: Update, context: CallbackContext, order_id: int) -> int:
    tg_user = update.effective_user
    bot = context.bot
    query = update.callback_query
    message = query.message
    order: Order = OrderClient.delivered(order_id, tg_user.id)
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
            order.supplier_id,
            f'Заказ с номером {order_id} перешел в состояние <i>'
            f'{OrderStatuses.get_by_name(order.status).label}</i>, ЗАКРЫТ',
            parse_mode=ParseMode.HTML
        )
        cc_msg = f'Дякуємо за замовлення, bon appetit! =)'
        bot.send_animation(
            chat_id=order.owner_id,
            animation=gif(order.status),
            caption=cc_msg,
            parse_mode=ParseMode.HTML,
        )
        return MAIN_MENU_DELIVER


DELIVER_STATUS_HANDLERS = {
    OrderStatuses.ASSIGNED_DEL.code: assign_delivery,
    OrderStatuses.GOING.code: going_delivery,
    OrderStatuses.ARRIVED.code: arrived_delivery,
    OrderStatuses.DELIVERED.code: delivered_delivery,
}
