class CallbackPatterns:
    position_add_pattern = (r"^mp_\d+_add_callback$", 'mp_id_add_callback')
    position_remove_pattern = (r"^mp_\d+_del_callback$", 'mp_id_del_callback')

    order_supplier_fl_callback = (r"^osa_\d+_(full|less)_callback$", 'osa_id_fl_callback')
    order_supplier_move_state_callback = (r"^osa_\d+_\d+_status_callback$", 'osa_id_code_status_callback')
    order_supplier_cancel_callback = (r"^osa_\d+_cancel_callback$", 'osa_id_cancel_callback')
    order_supplier_open_callback = (r"^osa_\d+_open_callback$", 'osa_id_open_callback')

    order_notify_confirm = (r'^onc_\d+_\d{2}:\d{2}_notify_callback$', 'onc_id_time_notify_callback')

