import logging
from functools import wraps
from typing import Callable, List

from telegram import Update
from telegram.ext import CallbackContext


def restrict(admin_ids: List) -> Callable:
    """This is a decorator for telegram handlers which allow wrapped function call only for admins"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(self, update: Update, context: CallbackContext, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id not in admin_ids:
                logging.getLogger().warning("Unauthorized access denied for {}.".format(user_id))
                context.bot.send_message(chat_id=update.effective_chat.id, text="This is not allowed")
                return
            return func(self, update, context, *args, **kwargs)

        return wrapped

    return decorator


__all__ = ["restrict"]
