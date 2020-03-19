from functools import wraps
from typing import Callable

from telegram import ChatAction, Update
from telegram.ext import CallbackContext


def send_action(action: ChatAction):
    """Sends `action` while processing function command."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def command_func(self, update: Update, context: CallbackContext, *args, **kwargs) -> Callable:
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(self, update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)

__all__ = ["send_typing_action"]
