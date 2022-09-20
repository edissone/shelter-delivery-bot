from typing import Union, List


class Roles:
    CUSTOMER = 'CUSTOMER'
    SUPPLIER = 'SUPPLIER'
    DELIVER = 'DELIVER'


class DeliveryTypes:
    DELIVERY = 'DELIVERY'
    SELF = 'SELF'


class PaymentType:
    CARD = ('CARD', 'Безналичный')
    CASH = ('CASH', 'Наличный')


class StatusItem:
    def __init__(self, name: str, label: str, code: int, active: bool, role: str = None):
        self.name = name
        self.label = label
        self.code = code
        self.active = active,
        self.role = role


class OrderStatuses:
    CREATED = StatusItem('CREATED', 'Создан', 100, True)
    ASSIGNED = StatusItem('ASSIGNED', 'В обработке', 110, True, Roles.SUPPLIER)
    CONFIRM = StatusItem('CONFIRM', 'Подтвержден', 200, True, Roles.SUPPLIER)
    PREPARING = StatusItem('PREPARING', 'Готовится', 210, True, Roles.SUPPLIER)
    READY_DEL = StatusItem('READY_DEL', 'Готов для доставки', 300, True, Roles.SUPPLIER)
    READY_SELF = StatusItem('READY_SELF', 'Готов для самовывоза', 310, True, Roles.SUPPLIER)
    GOING = StatusItem('GOING', 'В пути', 400, True, Roles.DELIVER)
    DELIVERED = StatusItem('DELIVERED', 'Доставлен', 500, False, Roles.DELIVER)
    GOT_SELF = StatusItem('GOT_SELF', 'Забран', 510, False, Roles.SUPPLIER)
    DECLINED_CUSTOMER = StatusItem('DECLINED_CUSTOMER', 'Отменен клиентом', -100, False)
    DECLINED_SUPPLIER = StatusItem('DECLINED_SUPPLIER', 'Отменен оператором', -200, False)
    DECLINED_DELIVER = StatusItem('DECLINED_DELIVER', 'Отменен доставщиком', -300, False)

    __list = [CREATED, ASSIGNED, CONFIRM, PREPARING, READY_DEL, READY_SELF, GOING, DELIVERED,
              GOT_SELF, DECLINED_CUSTOMER, DECLINED_SUPPLIER, DECLINED_DELIVER]

    __workflows = {
        f'{PaymentType.CARD[0]}/{DeliveryTypes.DELIVERY}': [100, 110, 200, 210, 300, 400, 500],
        f'{PaymentType.CASH[0]}/{DeliveryTypes.DELIVERY}': [100, 110, 210, 300, 400, 500],
        f'{PaymentType.CARD[0]}/{DeliveryTypes.SELF}': [100, 110, 200, 210, 310, 510],
        f'{PaymentType.CASH[0]}/{DeliveryTypes.SELF}': [100, 110, 210, 310, 510]
    }

    @classmethod
    def next(cls, status: str, payment_type: str, delivery_type: str, role: str) -> Union[StatusItem, None]:
        workflow: List = cls.__workflows[f'{payment_type}/{delivery_type}']
        current_index = workflow.index(cls.get_by_name(status).code)
        status = cls.get_by_code(workflow[current_index + 1]) if len(workflow) - current_index > 1 else None
        if status is not None:
            return status if status.role == role else cls.next(status.name, payment_type, delivery_type, role)
        else:
            return status

    @classmethod
    def previous(cls, status_name: str, payment_type: str, delivery_type: str, role: str) -> Union[StatusItem, None]:
        workflow: List = cls.__workflows[f'{payment_type}/{delivery_type}']
        current_status = cls.get_by_name(status_name)
        current_index = workflow.index(current_status.code)
        status = cls.get_by_code(workflow[current_index - 1]) if current_index > 0 else None
        if status is not None:
            result = status if status.role == role else \
                cls.previous(status.name, payment_type, delivery_type, role)
            return result if result is not None and result.active else None
        else:
            return status

    @classmethod
    def get_by_code(cls, code: int) -> Union[StatusItem, None]:
        for os in cls.__list:
            if os.code == code:
                return os
        return None

    @classmethod
    def get_by_name(cls, name: str) -> Union[StatusItem, None]:
        for os in cls.__list:
            if os.name == name:
                return os
        return None
