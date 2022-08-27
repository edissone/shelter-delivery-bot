from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from src.handlers import Handlers
from src.handlers.menu import MenuHandlers
from src.handlers.order import OrderHandlers
from src.handlers.register import RegisterHandlers
from src.handlers.states import REGISTER_NAME, REGISTER_PHONE, REGISTER_CONFIRM, REGISTER_START, MAIN_MENU_CUSTOMER, \
    MENU_CATEGORIES, ORDER_CONFIRM_POSITIONS, ORDER_DELIVERY_TYPE, ORDER_DELIVERY_NAME, ORDER_DELIVERY_PHONE, \
    ORDER_DELIVERY_ADDRESS, ORDER_DELIVERY_NOTES, ORDER_NOTES, ORDER_PAYMENT_TYPE, ORDER_PAYMENT_PAYBACK_FROM, \
    ORDER_CONFIRM
from src.keyboards.callback_patterns import CallbackPatterns

registration_start = MessageHandler(Filters.text, RegisterHandlers.register_start)
registration_name = MessageHandler(Filters.text, RegisterHandlers.register_name)
registration_phone_text = MessageHandler(Filters.text, RegisterHandlers.register_phone_text)
registration_phone_contact = MessageHandler(Filters.contact, RegisterHandlers.register_phone_contact)
registration_confirm = MessageHandler(Filters.text, RegisterHandlers.register_confirm)

main_menu_customer = MessageHandler(Filters.text, MenuHandlers.main_menu_customer)
menu_categories = MessageHandler(Filters.text, MenuHandlers.menu_get_positions)
add_position = CallbackQueryHandler(callback=MenuHandlers.add_position,
                                    pattern=CallbackPatterns.position_add_pattern[0])
remove_position = CallbackQueryHandler(callback=MenuHandlers.remove_position,
                                       pattern=CallbackPatterns.position_remove_pattern[0])

order_confirm = MessageHandler(Filters.text, OrderHandlers.order_confirm)
order_notes = MessageHandler(Filters.text, OrderHandlers.order_notes)

order_delivery_type = MessageHandler(Filters.text, OrderHandlers.order_delivery_type)
order_delivery_name = MessageHandler(Filters.text, OrderHandlers.order_delivery_name)
order_delivery_phone = MessageHandler(Filters.text, OrderHandlers.order_delivery_phone)
order_delivery_address = MessageHandler(Filters.text, OrderHandlers.order_delivery_address)
order_delivery_notes = MessageHandler(Filters.text, OrderHandlers.order_delivery_notes)

order_payment_type = MessageHandler(Filters.text, OrderHandlers.order_payment_type)
order_payment_payback_from = MessageHandler(Filters.text, OrderHandlers.order_payment_payback_from)

customer_states = {
    REGISTER_START: [registration_start],
    REGISTER_NAME: [registration_name],
    REGISTER_PHONE: [registration_phone_text, registration_phone_contact],
    REGISTER_CONFIRM: [registration_confirm],

    MAIN_MENU_CUSTOMER: [main_menu_customer],
    MENU_CATEGORIES: [menu_categories, add_position, remove_position],

    ORDER_CONFIRM_POSITIONS: [order_confirm],
    ORDER_NOTES: [order_notes],
    ORDER_DELIVERY_TYPE: [order_delivery_type],
    ORDER_DELIVERY_NAME: [order_delivery_name],
    ORDER_DELIVERY_PHONE: [order_delivery_phone],
    ORDER_DELIVERY_ADDRESS: [order_delivery_address],
    ORDER_DELIVERY_NOTES: [order_delivery_notes],

    ORDER_PAYMENT_TYPE: [order_payment_type],
    ORDER_PAYMENT_PAYBACK_FROM: [order_payment_payback_from],
    ORDER_CONFIRM: []
}

supplier_states = {}

deliver_states = {}

states = {
    **customer_states,
    **supplier_states,
    **deliver_states
}


class Bot:
    def __init__(self, token: str):
        self.token = token
        self.updater = Updater(token)
        self.updater.dispatcher.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler('start', Handlers.start)],
                allow_reentry=True,
                states=states,
                fallbacks=[CommandHandler('start', Handlers.start)]
            )
        )
