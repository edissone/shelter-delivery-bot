import re


class Validator:
    __phone_regex = r"^(?:\+38)0\d{9}$"

    @staticmethod
    def is_phone_number(number: str) -> bool:
        s = re.findall(Validator.__phone_regex, number)
        return number in s