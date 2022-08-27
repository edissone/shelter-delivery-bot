class CallbackPatterns:
    position_add_pattern = (r"^mp_\d+_add_callback$", 'mp_id_add_callback')
    position_remove_pattern = (r"^mp_\d+_del_callback$", 'mp_id_del_callback')
