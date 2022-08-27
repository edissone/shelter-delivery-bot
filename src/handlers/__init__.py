from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from src.client.user import UserClient
from src.handlers.states import REGISTER_START, NULL_STATE, MAIN_MENU_CUSTOMER
from src.messages.menu import MenuMessages
from src.messages.register import RegisterMessages
from src.models.const import Roles
from src.models.dto import User
from src.utils.exceptions import NotFoundException


class Handlers:
    @classmethod
    def start(cls, update: Update, context: CallbackContext) -> int:
        tg_user = update.effective_user
        bot = context.bot
        user: User
        try:
            user = UserClient.get(tg_user.id)
        except NotFoundException:
            msg, keyboard = RegisterMessages.register()
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return REGISTER_START
        if user.role == Roles.CUSTOMER:
            msg, keyboard = MenuMessages.main_menu(user.role)
            bot.send_message(tg_user.id, msg, parse_mode=ParseMode.HTML, reply_markup=keyboard)
            return MAIN_MENU_CUSTOMER
