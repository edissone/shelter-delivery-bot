from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from src.keyboards import Keyboards
from src.keyboards.callback_patterns import CallbackPatterns


class ReportKeyboards(Keyboards):
    @classmethod
    def report_option(cls) -> InlineKeyboardMarkup:
        keyboard = [
            InlineKeyboardButton(text='За сегодня',
                                 callback_data=CallbackPatterns.report_supplier_callback[1].replace('opt', str(0))),
            InlineKeyboardButton(text='За текущий месяц',
                                 callback_data=CallbackPatterns.report_supplier_callback[1].replace('opt', str(1))),
            InlineKeyboardButton(text='За все время',
                                 callback_data=CallbackPatterns.report_supplier_callback[1].replace('opt', str(2)))
        ]
        return InlineKeyboardMarkup.from_column(keyboard)
