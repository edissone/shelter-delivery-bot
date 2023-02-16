from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from src.client.user import UserClient
from src.handlers.states import REGISTER_NAME, REGISTER_START, REGISTER_PHONE, REGISTER_CONFIRM, MAIN_MENU_CUSTOMER
from src.messages.register import RegisterMessages
from src.models.const import Roles
from src.models.dto import User
from src.utils.cache import Cache
from src.utils.exceptions import ServiceException
from src.utils.logger import log
from src.utils.validator import Validator

USER_TO_CREATE = 'user_to_create'


class RegisterHandlers:
    @classmethod
    def register_start(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        if message.text == 'Зареєструватись 📁':
            log.info(f'registration new user: {tg_user.id}')
            cache = Cache.get(tg_user.id)
            cache[USER_TO_CREATE] = User(tg_id=tg_user.id, role=Roles.CUSTOMER)
            msg, keyboard = RegisterMessages.register_start()
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return REGISTER_NAME
        else:
            err_msg = "Не могу понять.\nПопробуй еще раз."
            bot.send_message(tg_user.id, err_msg)
            return REGISTER_START

    @classmethod
    def register_name(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        message = update.effective_message
        cache = Cache.get(tg_user.id)
        user = cache[USER_TO_CREATE]
        user.full_name = message.text
        msg, keyboard = RegisterMessages.register_name(user.full_name)
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return REGISTER_PHONE

    @classmethod
    def register_phone_contact(cls, update: Update, context: CallbackContext) -> int:
        contact = update.effective_message.contact
        phone = f'+{contact.phone_number}'
        return cls.__register_phone(update, context, phone)

    @classmethod
    def register_phone_text(cls, update: Update, context: CallbackContext) -> int:
        text = update.effective_message.text
        tg_user = update.effective_user
        bot = context.bot
        if text is not None and Validator.is_phone_number(text):
            phone = text
            return cls.__register_phone(update, context, phone)
        else:
            err_msg = 'Неверный формат номера. Попробуйте еще раз.'
            bot.send_message(tg_user.id, err_msg)
            return REGISTER_PHONE

    @classmethod
    def __register_phone(cls, update: Update, context: CallbackContext, phone: str) -> int:
        tg_user = update.effective_user
        bot = context.bot
        cache = Cache.get(tg_user.id)
        user = cache[USER_TO_CREATE]
        user.phone = phone
        msg, keyboard = RegisterMessages.register_phone(user)
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return REGISTER_CONFIRM

    @classmethod
    def register_confirm(cls, update: Update, context: CallbackContext) -> int:
        operation = update.effective_message.text
        if operation == 'Підтвердити ✅':
            return cls.__register_confirm(update, context)
        if operation == 'Змінити 🔄':
            return cls.__register_amend(update, context)

    @classmethod
    def __register_amend(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        msg, keyboard = RegisterMessages.register_start()
        bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return REGISTER_NAME

    @classmethod
    def __register_confirm(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        cache = Cache.get(tg_user.id)
        user = cache[USER_TO_CREATE]
        try:
            response = UserClient.create(user)
            if isinstance(response, User):
                log.info(f'successful registration for user: {response.tg_id}')
        except ServiceException as se:
            err_msg = 'Пиздец, сломалось :(.'
            msg, keyboard = RegisterMessages.register()
            log.exception(f'failed registration for user:{tg_user.id}: {se.error_message}')
            bot.send_message(tg_user.id, err_msg)
            bot.send_message(tg_user.id, msg, reply_markup=keyboard)
            return REGISTER_START
        del cache[USER_TO_CREATE]
        msgs, keyboard = RegisterMessages.register_confirm()
        for msg in msgs[:-1]:
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML)
        bot.send_message(tg_user.id, msgs[-1], reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return MAIN_MENU_CUSTOMER
