from datetime import datetime
from typing import List

from src.models import Serializable
from src.models.const import DeliveryTypes, PaymentType, OrderStatuses


class User(Serializable):
    def __init__(self, id: str = None, tg_id: str = None, phone: str = None, full_name: str = None, role: str = None,
                 address: str = None):
        self.id = id
        self.tg_id = tg_id
        self.phone = phone
        self.full_name = full_name
        self.role = role
        self.address = address


class DeliveryInfo(Serializable):
    def __init__(self, address: str = None, full_name: str = None, phone: str = None, notes: str = None):
        self.address = address
        self.full_name = full_name
        self.phone = phone
        self.notes = notes


class PositionStub(Serializable):
    def __init__(self, id: int = None, count: int = None, price: float = None, name: str = None):
        self.id = id
        self.count = count
        self.price = price
        self.name = name


class OrderLog(Serializable):
    def __init__(self, status: str = None, date: datetime = None):
        self.status = status
        self.date = date


class Position(Serializable):
    def __init__(self, id: int = None, name: str = None, category: str = None, description: str = None,
                 price: float = None, weight: str = None, image: str = None):
        self.name = name
        self.category = category
        self.description = description
        self.price = price
        self.weight = weight
        self.id = id
        self.image = image


class Order(Serializable):
    def __init__(self, id: int = None, owner_id: str = None, supplier_id: str = None, delivery_id: str = None,
                 notes: str = None, amount: float = None, payback_from: float = None, payback: float = None,
                 payment_code: str = None, payment_type: str = None, delivery_type: str = None,
                 delivery_info: DeliveryInfo = None, positions: List[PositionStub] = None,
                 logs: List[OrderLog] = None, status: str = None):
        self.id = id
        self.owner_id = owner_id
        self.supplier_id = supplier_id
        self.delivery_id = delivery_id
        self.notes = notes
        self.amount = amount
        self.payback_from = payback_from
        self.payback = payback
        self.payment_code = payment_code
        self.payment_type = payment_type
        self.delivery_type = delivery_type
        self.delivery_info: DeliveryInfo = delivery_info
        self.positions: List[PositionStub] = positions if positions is not None else []
        self.logs: List[OrderLog] = logs
        self.status = status

    def full_info(self, supplier_name: str, delivery_name: str):
        result = ''
        result += f'Номер заказу:{self.id}\n'
        result += f'Клиент: {self.delivery_info.full_name}\n'
        result += f'Оператор: {supplier_name}\n' if supplier_name is not None else ''
        result += f'Статус: {OrderStatuses.get_by_name(self.status).label}\n'
        ps_list = ''
        for ps in self.positions:
            ps_list += f'{ps.name}: {ps.count} ед., по {ps.price} грн.\n'
        result += f'\n{ps_list}\n'
        result += self.info_delivery()
        result += f'\nСдача с: {self.payback_from}' if self.payment_type == PaymentType.CASH[0] else ''
        result += f'\n\nДоставщик: {delivery_name}\n'if delivery_name is not None else ''
        return result

    def owner_info(self):
        result = ''
        result += f'📝 Номер замовлення: {self.id}\n'
        result += f'Статус: {OrderStatuses.get_by_name(self.status).label}\n'
        ps_list = '\n'
        for ps in self.positions:
            ps_list += f'{ps.name}: {ps.count} ед., по {ps.price} грн.\n'
        result += ps_list + '\n'
        result += self.info_delivery()
        return result


    def info(self):
        result = ''
        result += f'Номер заказа: {self.id}\n'
        result += f'Клиент: {self.delivery_info.full_name}\n'
        result += f'Тип доставки: {"Доставка" if self.delivery_type == DeliveryTypes.DELIVERY else "Самовывоз"}\n'
        result += f'Статус: {OrderStatuses.get_by_name(self.status).label}\n'
        ps_list = '\n'
        for ps in self.positions:
           ps_list += f'{ps.name}: {ps.count} ед., по {ps.price} грн.\n'
        result += ps_list
        return result

    def info_delivery(self):
        result = ''
        result += f'📝 Нотатки до замовлення: {"Відсутні" if self.notes is None else self.notes}\n'
        result += f'📦 Тип доставки: {"Доставка" if self.delivery_type == DeliveryTypes.DELIVERY else "Самовивіз"}\n'
        delivery_info = ''
        delivery_info += f'👤 Імʼя отримувача: {self.delivery_info.full_name}\n'
        delivery_info += f'📞 Номер отримувача: {self.delivery_info.phone}\n'
        if self.delivery_type == DeliveryTypes.DELIVERY:
            delivery_info += f'🏠 Адреса доставки: {self.delivery_info.address}\n'
            delivery_info += f'📝 Нотатки для курʼєра: {"Відсутні" if self.delivery_info.notes is None else self.delivery_info.notes}\n'
        result += delivery_info
        payment_type = ''
        payment_type += f'💰 Тип оплати: {PaymentType.CARD[1] if self.payment_type == PaymentType.CARD[0] else PaymentType.CASH[1]}\n'
        if payment_type == PaymentType.CASH[0]:
            payment_type += f'💵 Решта з:{self.payback_from}\n'
        payment_type += f'💸 Сума замовлення: {self.amount}'
        result += payment_type
        return result

    def info_delivery_stub(self):
        result = ''
        delivery_info = ''
        delivery_info += f'Имя получателя: {self.delivery_info.full_name}\n'
        delivery_info += f'Номер получателя: {self.delivery_info.phone}\n'
        delivery_info += f'Адрес доставки: {self.delivery_info.address}\n'
        delivery_info += f'Заметки к доставке: {"Отсутствуют" if self.delivery_info.notes is None else self.delivery_info.notes}\n'
        result += delivery_info
        payment_type = ''
        payment_type += f'Тип оплаты: {PaymentType.CARD[1] if self.payment_type == PaymentType.CARD[0] else PaymentType.CASH[1]}\n'
        if payment_type == PaymentType.CASH[0]:
            payment_type += f'Сдача с:{self.payback_from}\n'
        payment_type += f'Сумма заказа: {self.amount}'
        result += payment_type
        ps_list = '\n'
        for ps in self.positions:
            ps_list += f'{ps.name}: {ps.count} ед., по {ps.price} грн.\n'
        result += ps_list
        return result

    def add_position_stub(self, position: Position):
        exist = False
        for ps in self.positions:
            if ps.id == position.id:
                ps.count += 1
                exist = True
        if not exist:
            self.positions.append(PositionStub(position.id, 1))

    def remove_position_stub(self, position: Position):
        for ps in self.positions:
            if ps.id == position.id:
                if ps.count > 1:
                    ps.count -= 1
                else:
                    self.positions.remove(ps)
