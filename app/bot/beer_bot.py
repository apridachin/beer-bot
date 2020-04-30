import os
import sys
import traceback
from threading import Thread
from requests import HTTPError
from typing import List, TypeVar

from telegram.ext.dispatcher import run_async
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
from app.entities import Brewery, Beer, Contact, BeerList
from app.settings import TELEGRAM_TOKEN, admins, devs
from app.utils.build_menu import build_menu
from app.utils.send_action import send_typing_action

TBeerBot = TypeVar("TBeerBot", bound="BeerBot")


class BeerBot(LoggerMixin):
    """A class used as telegram bot which is chatting with users"""

    def __init__(self, client) -> None:
        super().__init__()
        self._client = client
        self.updater: Updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
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

    @run_async
    @send_typing_action
    def _show_handlers(self, update: Update, context: CallbackContext) -> None:
        """Show all available commands"""
        text: str = f"This is what you can ask me to do:\n" f"/search - find beer by name"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    @run_async
    @send_typing_action
    def _unknown(self, update: Update, context: CallbackContext) -> None:
        """Send message if command is unknown"""
        self.logger.info("Unknown command")
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. 🤷",
        )

    @run_async
    @send_typing_action
    def _search_beer(self, update: Update, context: CallbackContext) -> None:
        """Search beer by name and show a result"""
        user_message: str = update.message.text
        self.logger.info(f"Search {user_message}")
        beer_name: str = user_message.replace("/search ", "")
        beers: BeerList = self._client.search_beer(beer_name)
        if len(beers) > 1:
            self._show_options(update, context, beers)
        elif len(beers) == 1:
            self._send_beer(update, context, beers[0])
        else:
            self.logger.info(f"Beer was not found {beer_name}")
            self._not_found(update, context)

    @run_async
    @send_typing_action
    def _not_found(self, update: Update, context: CallbackContext) -> None:
        """Send message that noting was found"""
        chat_id: str = update.effective_chat.id
        text: str = "Nothing found"
        context.bot.send_message(chat_id=chat_id, text=text)

    @run_async
    @send_typing_action
    def _send_beer(self, update: Update, context: CallbackContext, beer: Beer) -> None:
        """Send prepared beer to user"""
        beer_id: str = beer.id
        text: str = self._parse_beer_to_html(beer)
        self.put_beer_context(context, beer_id, beer)
        options: List[List[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton("Brewery", callback_data=f"info_{beer_id}_brewery"),
                InlineKeyboardButton("Similar", callback_data=f"info_{beer_id}_similar"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(options)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML, reply_markup=reply_markup,
        )
        self.logger.info(f"Beer was sent {beer_id}")

    @run_async
    @send_typing_action
    def _show_options(self, update: Update, context: CallbackContext, beers: BeerList) -> None:
        """Send beer options to user"""
        beer_options: List[InlineKeyboardButton] = [
            InlineKeyboardButton(beer.name, callback_data=f"beer_{beer.id}") for beer in beers
        ]
        reply_markup = InlineKeyboardMarkup(build_menu(beer_options, n_cols=3))
        if len(beer_options) > 0:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Choose your destiny 💀", reply_markup=reply_markup,
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Nothing found", reply_markup=reply_markup,
            )

    @run_async
    @send_typing_action
    def _select_beer(self, update: Update, context: CallbackContext) -> None:
        """Handler for choosing beer from search results"""
        query: CallbackQuery = update.callback_query
        beer_id = int(query.data.replace("beer_", ""))
        try:
            beer = self.get_beer_context(context, beer_id)
            if beer is None:
                beer: Beer = self._client.get_item(beer_id, item_type="beer")
            self._send_beer(update, context, beer)
            self.logger.info(f"Beer was selected {beer_id}")
        except HTTPError:
            self.logger.exception(f"Beer was not found {beer_id}")
            self._not_found(update, context)
        except AttributeError:
            self.logger.exception(f"Failed sending beer {beer_id}")
            self._not_found(update, context)

    @run_async
    @send_typing_action
    def _select_info(self, update: Update, context: CallbackContext) -> None:
        """Handler for choosing options from beer message"""
        query: CallbackQuery = update.callback_query
        [prefix, beer_id, command_name] = query.data.split("_")

        if command_name == "brewery":
            self.send_brewery(update, context, beer_id)
        else:
            self.send_similar(update, context, beer_id)

    def send_brewery(self, update: Update, context: CallbackContext, beer_id: int) -> None:
        try:
            result = self.get_brewery_context(context, beer_id)
            if result is None:
                result = self._client.get_brewery_by_beer(beer_id)
                self.put_brewery_context(context, beer_id, result)
            text = self._parse_brewery_to_html(result)
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)
            self.send_brewery_location(update, context, result)
        except KeyError:
            self._not_found(update, context)

    def send_similar(self, update: Update, context: CallbackContext, beer_id: int):
        try:
            beer = self.get_beer_context(context, beer_id)
            similar = beer.similar
            self._show_options(update, context, similar)
        except AttributeError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Nothing found")

    def send_brewery_location(self, update: Update, context: CallbackContext, brewery: Brewery) -> None:
        text = "🧭 Location"
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        context.bot.send_location(
            chat_id=update.effective_chat.id, latitude=brewery.location.lat, longitude=brewery.location.lng
        )

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

    def _parse_brewery_to_html(self, brewery: Brewery) -> str:
        """Preparing brewery for message"""
        name = brewery.name
        b_type = brewery.brewery_type
        country = brewery.country
        description = brewery.description
        rating = brewery.rating
        raters = brewery.raters
        contact = brewery.contact

        links = self._parse_contact_to_string(contact)

        text = (
            f'🏠🏠🏠 <b>"{name}"</b> 🏠🏠🏠\n'
            f"\n️💅 <b>Type</b>:\n{b_type}\n"
            f"\n🏴 <b>Country</b>:\n{country}\n"
            f"\n️✍️ <b>Description</b>:\n{description}\n"
            f"\n⭐️ <i>Rating {rating}\n👫 Raters {raters}</i> \n"
            f"\n<b>Contacts</b>:\n{links}\n"
        )

        return text

    def _parse_contact_to_string(self, contact: Contact) -> str:
        text = ""
        try:
            url = contact.url
            twitter = contact.twitter
            facebook = contact.facebook
            text = f"️🕸 Site: {url}\n" f"💬 Twitter: {twitter}\n" f"🙍‍♀️Facebook: {facebook}\n"
        except KeyError:
            self.logger.error(f"Failed to parse brewery contact {contact}")
        finally:
            return text

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

    def get_beer_key(self, key):
        return f"beer_{key}"

    def get_brewery_key(self, key):
        return f"brewery_{key}"

    def put_beer_context(self, context: CallbackContext, key, value):
        beer_key = self.get_beer_key(key)
        self.put_context_item(context, beer_key, value)

    def get_beer_context(self, context: CallbackContext, key):
        beer_key = self.get_beer_key(key)
        return self.get_context_item(context, beer_key)

    def put_brewery_context(self, context: CallbackContext, key, value):
        beer_key = self.get_brewery_key(key)
        self.put_context_item(context, beer_key, value)

    def get_brewery_context(self, context: CallbackContext, key):
        brewery_key = self.get_brewery_key(key)
        return self.get_context_item(context, brewery_key)

    def put_context_item(self, context: CallbackContext, key, value):
        context.user_data[str(key)] = value

    def get_context_item(self, context: CallbackContext, key):
        return context.user_data.get(key, None)
