from src.keyboards.report import ReportKeyboards
from src.messages import Messages


class ReportMessages(Messages):
    @classmethod
    def report_option(cls):
        msg = 'Выберите период ...'
        keyboard = ReportKeyboards.report_option()
        return msg, keyboard
