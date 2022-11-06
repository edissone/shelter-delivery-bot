from telegram import ReplyKeyboardMarkup, KeyboardButton

from src.keyboards import Keyboards


class RegisterKeyboards(Keyboards):
    class Reply:
        @classmethod
        def register(cls) -> ReplyKeyboardMarkup:
            keyboard = [KeyboardButton('Зареєструватись 📁')]
            return ReplyKeyboardMarkup.from_row(keyboard, resize_keyboard=True)

        @classmethod
        def register_name(cls) -> ReplyKeyboardMarkup:
            keyboard = [KeyboardButton('Поділитись контактом 📲', request_contact=True)]
            return ReplyKeyboardMarkup.from_row(keyboard, resize_keyboard=True)

        @classmethod
        def register_phone(cls) -> ReplyKeyboardMarkup:
            keyboard = [
                [KeyboardButton('Підтвердити ✅')],
                [KeyboardButton('Змінити 🔄')]
            ]
            return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
