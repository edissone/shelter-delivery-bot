from typing import Tuple, List

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.keyboards.register import RegisterKeyboards
from src.messages import Messages
from src.messages.menu import MenuMessages
from src.models.const import Roles
from src.models.dto import User


class RegisterMessages(Messages):
    @classmethod
    def register(cls) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('register/register')
        keyboard = RegisterKeyboards.Reply.register()
        return msg, keyboard

    @classmethod
    def register_start(cls) -> Tuple[str, ReplyKeyboardRemove]:
        msg = Messages._read_message_text('register/register_start')
        keyboard = RegisterKeyboards.remove()
        return msg, keyboard

    @classmethod
    def register_name(cls, full_name) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = Messages._read_message_text('register/register_name').replace('$full_name$', full_name)
        keyboard = RegisterKeyboards.Reply.register_name()
        return msg, keyboard

    @classmethod
    def register_phone(cls, user: User) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = Messages._read_message_text('register/register_phone') \
            .replace('$full_name$', user.full_name) \
            .replace('$phone$', user.phone)
        keyboard = RegisterKeyboards.Reply.register_phone()
        return msg, keyboard

    @classmethod
    def register_confirm(cls) -> Tuple[List[str], ReplyKeyboardMarkup]:
        menu_msg, keyboard = MenuMessages.main_menu(Roles.CUSTOMER)
        msgs = [
            cls._read_message_text('register/register_confirm'),
            menu_msg
        ]
        return msgs, keyboard
