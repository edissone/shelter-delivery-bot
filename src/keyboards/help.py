from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.keyboards import Keyboards


class HelpKeyboards(Keyboards):
    @classmethod
    def help_menu(cls, map_link, inst_link, bond_link) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="Перевірити регіон доставки 🗺", url=map_link)],
            [InlineKeyboardButton(text="Інстаграм 📷", url=inst_link),
             InlineKeyboardButton(text="Bond Delivery 🚚", url=bond_link)]
        ]
        return InlineKeyboardMarkup(keyboard)
