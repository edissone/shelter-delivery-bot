from typing import Tuple, List

from telegram import InlineKeyboardMarkup

from src.keyboards.help import HelpKeyboards
from src.messages import Messages
from src.models.const import resource_params


class HelpMessages(Messages):
    @classmethod
    def help_menu(cls) -> Tuple[List[str], InlineKeyboardMarkup]:
        msg_raw = cls._read_message_text('help/help_menu').replace("$address$", resource_params['address']) \
            .replace("$work_time$", resource_params['work_time']).replace("$support_contact$", resource_params['support_contact'])
        msgs = cls._prepare_message(msg_raw)
        keyboard = HelpKeyboards.help_menu(resource_params['map_link'], resource_params['inst_link'],
                                           resource_params['bond_link'])
        return msgs, keyboard
