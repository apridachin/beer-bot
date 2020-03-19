def build_menu(buttons, n_cols: int, header_buttons=None, footer_buttons=None):
    """Function creates menu for telegram with header and footer if they are presented"""
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


__all__ = ["build_menu"]
