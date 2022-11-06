from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from src.handlers import Handlers
from src.handlers.menu import MenuHandlers
from src.handlers.order import OrderHandlers
from src.handlers.register import RegisterHandlers
from src.handlers.states import REGISTER_NAME, REGISTER_PHONE, REGISTER_CONFIRM, REGISTER_START, MAIN_MENU_CUSTOMER, \
    MENU_CATEGORIES, ORDER_CONFIRM_POSITIONS, ORDER_DELIVERY_TYPE, ORDER_DELIVERY_NAME, ORDER_DELIVERY_PHONE, \
    ORDER_DELIVERY_ADDRESS, ORDER_DELIVERY_NOTES, ORDER_NOTES, ORDER_PAYMENT_TYPE, ORDER_PAYMENT_PAYBACK_FROM, \
    ORDER_CONFIRM, MAIN_MENU_SUPPLIER, MAIN_MENU_DELIVER
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

order_confirm_create = MessageHandler(Filters.text, OrderHandlers.order_confirm_create)
order_notes = MessageHandler(Filters.text, OrderHandlers.order_notes)

order_delivery_type = MessageHandler(Filters.text, OrderHandlers.order_delivery_type)
order_delivery_name = MessageHandler(Filters.text, OrderHandlers.order_delivery_name)
order_delivery_phone = MessageHandler(Filters.text, OrderHandlers.order_delivery_phone)
order_delivery_address = MessageHandler(Filters.text, OrderHandlers.order_delivery_address)
order_delivery_notes = MessageHandler(Filters.text, OrderHandlers.order_delivery_notes)

order_payment_type = MessageHandler(Filters.text, OrderHandlers.order_payment_type)
order_payment_payback_from = MessageHandler(Filters.text, OrderHandlers.order_payment_payback_from)
order_escalate_confirm = CallbackQueryHandler(callback=OrderHandlers.escalate_confirm,
                                              pattern=CallbackPatterns.order_notify_confirm[0])

order_confirm = MessageHandler(Filters.text, OrderHandlers.order_confirm)

order_owner_cancel_callback = CallbackQueryHandler(callback=OrderHandlers.order_owner_cancel_callback,
                                                   pattern=CallbackPatterns.order_owner_cancel_callback[0])

main_menu_supplier = MessageHandler(Filters.text, MenuHandlers.main_menu_supplier)

supplier_move_to_state_callback = CallbackQueryHandler(callback=MenuHandlers.supplier_move_to_state_callback,
                                                       pattern=CallbackPatterns.order_supplier_move_state_callback[0])
supplier_fl_order_info_callback = CallbackQueryHandler(callback=MenuHandlers.supplier_fl_order_info,
                                                       pattern=CallbackPatterns.order_supplier_fl_callback[0])
supplier_cancel_callback = CallbackQueryHandler(callback=MenuHandlers.supplier_cancel_callback,
                                                pattern=CallbackPatterns.order_supplier_cancel_callback[0])
deliver_cancel_callback = CallbackQueryHandler(callback=MenuHandlers.deliver_cancel_callback,
                                               pattern=CallbackPatterns.order_deliver_cancel_callback[0])
deliver_main_menu = MessageHandler(Filters.text, MenuHandlers.main_menu_delivery)
deliver_move_to_state_callback = CallbackQueryHandler(callback=MenuHandlers.deliver_move_to_state_callback,
                                                      pattern=CallbackPatterns.order_deliver_move_state_callback[0])

customer_states = {
    REGISTER_START: [registration_start],
    REGISTER_NAME: [registration_name],
    REGISTER_PHONE: [registration_phone_text, registration_phone_contact],
    REGISTER_CONFIRM: [registration_confirm],

    MAIN_MENU_CUSTOMER: [main_menu_customer, order_escalate_confirm, order_owner_cancel_callback],
    MENU_CATEGORIES: [menu_categories, add_position, remove_position, order_escalate_confirm,
                      order_owner_cancel_callback],

    ORDER_CONFIRM_POSITIONS: [order_confirm_create],
    ORDER_NOTES: [order_notes],
    ORDER_DELIVERY_TYPE: [order_delivery_type],
    ORDER_DELIVERY_NAME: [order_delivery_name],
    ORDER_DELIVERY_PHONE: [order_delivery_phone],
    ORDER_DELIVERY_ADDRESS: [order_delivery_address],
    ORDER_DELIVERY_NOTES: [order_delivery_notes],

    ORDER_PAYMENT_TYPE: [order_payment_type],
    ORDER_PAYMENT_PAYBACK_FROM: [order_payment_payback_from],
    ORDER_CONFIRM: [order_confirm]
}

supplier_states = {
    MAIN_MENU_SUPPLIER: [main_menu_supplier, supplier_move_to_state_callback, supplier_fl_order_info_callback,
                         supplier_cancel_callback]
}

deliver_states = {
    MAIN_MENU_DELIVER: [deliver_main_menu, deliver_move_to_state_callback, deliver_cancel_callback]
}

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
        self.updater.dispatcher.add_handler(
            CommandHandler('help', Handlers.help)
        )
