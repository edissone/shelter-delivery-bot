from typing import Tuple, List

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup

from src.keyboards.menu import MenuKeyboards
from src.messages import Messages
from src.models.dto import Position


class MenuMessages(Messages):
    @classmethod
    def main_menu(cls, role: str) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('menu/main_menu')
        keyboard = MenuKeyboards.Reply.main_menu(role)
        return msg, keyboard

    @classmethod
    def menu_categories(cls, categories: List[str]) -> Tuple[str, ReplyKeyboardMarkup]:
        msg = cls._read_message_text('menu/categories')
        keyboard = MenuKeyboards.Reply.menu_categories(categories)
        return msg, keyboard

    @classmethod
    def menu_get_position(cls, position: Position, in_order: bool) -> Tuple[str, InlineKeyboardMarkup]:
        msg = cls._read_message_text('menu/position_info') \
            .replace('$name$', position.name) \
            .replace('$description$', position.description) \
            .replace('$price$', str(position.price)) \
            .replace('$weight$', position.weight)
        keyboard = MenuKeyboards.Inline.menu_get_position(position, in_order)
        return msg, keyboard

    @classmethod
    def notify_confirm(cls, code: str, order_id: int, time: str, card: str) -> Tuple[str, InlineKeyboardMarkup]:
        msg = cls._read_message_text('menu/notify_confirm').replace('$code$', code).replace('$card$', card)
        keyboard = MenuKeyboards.Inline.notify_confirm(order_id, time)
        return msg, keyboard
