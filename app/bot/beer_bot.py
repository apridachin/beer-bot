import os
import sys
import traceback
from threading import Thread
from requests import HTTPError
from typing import List, TypeVar

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from telegram.utils.helpers import mention_html

from app.logging import LoggerMixin
from app.types import Beer, TBeerList
from app.settings import TelegramToken, admins, devs
from app.utils.build_menu import build_menu
from app.utils.send_action import send_typing_action
from app.untappd.client import TUntappdClient

TBeerBot = TypeVar("TBeerBot", bound="BeerBot")


class BeerBot(LoggerMixin):
    """A class used as telegram bot which is chatting with users"""

    def __init__(self, client: TUntappdClient) -> None:
        super().__init__()
        self._client: TUntappdClient = client
        self.updater: Updater = Updater(token=TelegramToken, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Commands
        self.show_handler: CommandHandler = CommandHandler("list", self._show_handlers)
        self.search_handler: CommandHandler = CommandHandler("search", self._search_beer)
        self.select_info_handler: CallbackQueryHandler = CallbackQueryHandler(self._select_info, pattern="info")
        self.select_beer_handler: CallbackQueryHandler = CallbackQueryHandler(self._select_beer, pattern="beer")
        self.restart_handler: CommandHandler = CommandHandler(
            "restart", self.restart, filters=Filters.user(username=admins)
        )
        self.unknown_handler: MessageHandler = MessageHandler(Filters.command, self._unknown)

        # Registered handlers
        self.dispatcher.add_handler(self.show_handler)
        self.dispatcher.add_handler(self.search_handler)
        self.dispatcher.add_handler(self.select_info_handler)
        self.dispatcher.add_handler(self.select_beer_handler)
        self.dispatcher.add_handler(self.restart_handler)
        self.dispatcher.add_handler(self.unknown_handler)
        self.dispatcher.add_error_handler(self.handle_error)

    def run(self):
        """Public method to start a bot"""
        self.updater.start_polling()
        self.logger.info("Bot has been started")

    def stop_and_restart(self):
        """Gracefully stop the Updater and replace the current process with a new one"""
        self.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)
        self.logger.info("Bot has been restarted")

    def restart(self, update: Update) -> None:
        """Public method to restart a bot"""
        update.message.reply_text("Bot is restarting... ♻️")
        Thread(target=self.stop_and_restart).start()
        update.message.reply_text("Bot is ready! 🤖")

    @send_typing_action
    def _show_handlers(self, update: Update, context: CallbackContext) -> None:
        """Show all available commands"""
        text: str = f"This is what you can ask me to do:\n" f"/search - find beer by name"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    @send_typing_action
    def _unknown(self, update: Update, context: CallbackContext) -> None:
        """Send message if command is unknown"""
        self.logger.info("Unknown command")
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. 🤷",
        )

    @send_typing_action
    def _search_beer(self, update: Update, context: CallbackContext) -> None:
        """Search beer by name and show a result"""
        user_message: str = update.message.text
        self.logger.info(f"Search {user_message}")
        beer_name: str = user_message.replace("/search ", "")
        beers: TBeerList = self._client.search_beer(beer_name)
        if len(beers) > 1:
            self._show_options(update, context, beers)
        elif len(beers) == 1:
            self._send_beer(update, context, beers[0])
        else:
            self.logger.info(f"Beer was not found {beer_name}")
            self._not_found(update, context)

    @send_typing_action
    def _not_found(self, update: Update, context: CallbackContext) -> None:
        """Send message that noting was found"""
        chat_id: str = update.effective_chat.id
        text: str = "Nothing found"
        context.bot.send_message(chat_id=chat_id, text=text)

    @send_typing_action
    def _send_beer(self, update: Update, context: CallbackContext, beer: Beer) -> None:
        """Send prepared beer to user"""
        chat_id: str = update.effective_chat.id
        beer_id: str = beer.id
        text: str = self._parse_beer_to_html(beer)
        options: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton("Brewery", callback_data=f"info_{beer_id}_brewery")],
            [InlineKeyboardButton("Similar", callback_data=f"info_{beer_id}_similar")],
            [InlineKeyboardButton("Locations", callback_data=f"info_{beer_id}_locations")],
        ]
        reply_markup = InlineKeyboardMarkup(options)
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Want to know more?", reply_markup=reply_markup,
        )
        self.logger.info(f"Beer was sent {beer_id}")

    @send_typing_action
    def _show_options(self, update: Update, context: CallbackContext, beers: TBeerList) -> None:
        """Send beer options to user"""
        beer_options: List[InlineKeyboardButton] = [
            InlineKeyboardButton(beer.name, callback_data=f"beer_{beer.id}") for beer in beers
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(beer_options, n_cols=3))
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Choose your destiny 💀", reply_markup=reply_markup,
        )

    @send_typing_action
    def _select_beer(self, update: Update, context: CallbackContext) -> None:
        """Handler for choosing beer from search results"""
        query: CallbackQuery = update.callback_query
        beer_id = int(query.data.replace("beer_", ""))
        try:
            beer: Beer = self._client.get_beer(beer_id)
            self._send_beer(update, context, beer)
            self.logger.info(f"Beer was selected {beer_id}")
        except HTTPError:
            self.logger.exception(f"Beer was not found {beer_id}")
            self._not_found(update, context)

    @send_typing_action
    def _select_info(self, update: Update, context: CallbackContext) -> None:
        """Handler for choosing options from beer message"""
        query: CallbackQuery = update.callback_query
        [prefix, beer_id, command_name] = query.data.split("_")
        client_mapping = {
            "brewery": self._client.get_brewery,
            "similar": self._client.get_similar,
            "locations": self._client.get_locations,
        }
        parse_mapping = {
            "brewery": self._parse_brewery,
            "similar": self._parse_similar,
            "locations": self._parse_locations,
        }

        try:
            result = client_mapping[command_name](beer_id)
            text = parse_mapping[command_name]()
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        except KeyError:
            self._not_found(update, context)

    def handle_error(self, update: Update, context: CallbackContext):
        """Error handler, reply user and send traceback to devs"""
        self.logger.error(f"An error occured {context.error}")
        if update.effective_message:
            text = (
                "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. "
                "My developer(s) will be notified."
            )
            update.effective_message.reply_text(text)

        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        payload: str = ""
        if update.effective_user:
            payload += f" with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}"

        if update.effective_chat:
            payload += f" within the chat <i>{update.effective_chat.title}</i>"
            if update.effective_chat.username:
                payload += f" (@{update.effective_chat.username})"

        if update.poll:
            payload += f" with the poll id {update.poll.id}."

        text = (
            f"The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" f"</code>"
        )

        for dev_id in devs:
            context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
        raise

    def _parse_brewery(self):
        pass

    def _parse_similar(self):
        pass

    def _parse_locations(self):
        pass

    def _parse_beer_to_html(self, beer: Beer) -> str:
        """Preparing beer for message"""
        name = beer.name
        abv = beer.abv
        ibu = beer.ibu
        style = beer.style
        desc = beer.description
        brewery = beer.brewery.name
        rating = beer.rating
        raters = beer.raters

        text = (
            f'🍺🍺🍺 <b>"{name}"</b> 🍺🍺🍺\n'
            f"\n📈 <i>ABV {abv}\n📉 IBU {ibu}</i> \n"
            f"\n️💅 <b>Style</b>:\n{style}\n"
            f"\n🏠 <b>Brewery</b>:\n{brewery}\n"
            f"\n️✍️ <b>Description</b>:\n{desc}\n"
            f"\n⭐️ <i>Rating {rating}\n👫 Raters {raters}</i> \n"
        )

        return text
