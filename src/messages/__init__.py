from typing import List


class Messages:
    @classmethod
    def _read_message_text(cls, message_title) -> str:
        msg: str
        with open(f'resources/messages/{message_title}.txt') as msg_file:
            msg = msg_file.read()
        return msg

    @classmethod
    def _prepare_message(cls, raw_msg: str) -> List[str]:
        msgs = raw_msg.split('##')
        return msgs
