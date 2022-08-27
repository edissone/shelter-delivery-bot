from telegram import ReplyKeyboardRemove


class Keyboards:
    @classmethod
    def remove(cls) -> ReplyKeyboardRemove:
        return ReplyKeyboardRemove()
