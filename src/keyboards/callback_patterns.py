class CallbackPatterns:
    position_add_pattern = (r"^mp_\d+_add_callback$", 'mp_id_add_callback')
    position_remove_pattern = (r"^mp_\d+_del_callback$", 'mp_id_del_callback')
    order_owner_cancel_callback = (r"^ooc_\d+_cancel_callback$", 'ooc_id_cancel_callback')

    order_supplier_fl_callback = (r"^osa_\d+_(full|less)_callback$", 'osa_id_fl_callback')
    order_supplier_move_state_callback = (r"^osa_\d+_\d+_status_callback$", 'osa_id_code_status_callback')
    order_supplier_cancel_callback = (r"^osa_\d+_cancel_callback$", 'osa_id_cancel_callback')
    order_supplier_open_callback = (r"^osa_\d+_open_callback$", 'osa_id_open_callback')
    report_supplier_callback = (r"^rst_\d_report_callback$", "rst_opt_report_callback")
    supplier_remove_user_callback = (r"^sru_\d+_remove_callback$", "sru_tgid_remove_callback")

    order_notify_confirm = (r"^onc_\d+_(\d{1}|\d{2}):(\d{1}|\d{2})_notify_callback$", 'onc_id_time_notify_callback')

    order_deliver_cancel_callback = (r"^oda_\d+_cancel_callback$", 'oda_id_cancel_callback')
    order_deliver_move_state_callback = (r"^oda_\d+_\d+_status_callback$", 'oda_id_code_status_callback')
