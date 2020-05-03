import os
import sys
import traceback
from threading import Thread
from requests import HTTPError

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.utils.helpers import mention_html

from app.settings import TelegramToken, Admins, Devs
from app.utils.build_menu import build_menu
from app.utils.send_action import send_typing_action


class BeerBot:
    def __init__(self, client):
        self._client = client
        self.updater = Updater(token=TelegramToken, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.show_handler = CommandHandler('list', self._show_handlers)
        self.random_handler = CommandHandler('random', self._random_beer)
        self.find_handler = CommandHandler('find', self._find_beer)
        self.search_handler = CommandHandler('search', self._search_beer)
        self.select_info_handler = CallbackQueryHandler(self._select_info, pattern='info')
        self.select_beer_handler = CallbackQueryHandler(self._select_beer, pattern='beer')
        self.restart_handler = CommandHandler('restart', self.restart, filters=Filters.user(username=Admins))
        self.unknown_handler = MessageHandler(Filters.command, self._unknown)

        self.dispatcher.add_handler(self.show_handler)
        self.dispatcher.add_handler(self.random_handler)
        self.dispatcher.add_handler(self.find_handler)
        self.dispatcher.add_handler(self.search_handler)
        self.dispatcher.add_handler(self.select_info_handler)
        self.dispatcher.add_handler(self.select_beer_handler)
        self.dispatcher.add_handler(self.restart_handler)
        self.dispatcher.add_handler(self.unknown_handler)
        self.dispatcher.add_error_handler(self.handle_error)

    def run(self):
        self.updater.start_polling()

    def stop_and_restart(self):
        """Gracefully stop the Updater and replace the current process with a new one"""
        self.updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(self, update, context):
        update.message.reply_text('Bot is restarting... ♻️')
        Thread(target=self.stop_and_restart).start()
        update.message.reply_text('Bot is ready! 🤖')

    @send_typing_action
    def _show_handlers(self, update, context):
        text = f'This is what you can ask me to do:\n' \
               f'/random - get random beer\n' \
               f'/search - find beer by name'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def _unknown(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command. 🤷")

    def _random_beer(self, update, context):
        beer = self._client.get_random()
        self._send_beer(beer, update, context)

    @send_typing_action
    def _search_beer(self, update, context):
        user_message = update.message.text
        beer_name = user_message.replace('/search ', '')
        beers = self._client.search_beer(beer_name)
        if len(beers) > 1:
            self._show_options(beers, update, context)
        elif len(beers) == 1:
            self._send_beer(beers[0], update, context)
        else:
            self._not_found(update, context)

    @send_typing_action
    def _find_beer(self, update, context):
        user_message = update.message.text
        beer_name = user_message.replace('/find ', '')
        beers = self._client.get_by_name(beer_name)

        if len(beers) > 1:
            self._show_options(beers, update, context)
        elif len(beers) == 1:
            self._send_beer(beers[0], update, context)
        else:
            self._not_found(update, context)

    @send_typing_action
    def _not_found(self, update: Updater, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = 'Nothing found'
        context.bot.send_message(chat_id=chat_id, text=text)

    @send_typing_action
    def _send_beer(self, beer, update: Updater, context: CallbackContext):
        chat_id = update.effective_chat.id
        beer_id = beer.get('id', '')
        text = self._parse_beer_to_html(beer)
        options = [[InlineKeyboardButton('Variations', callback_data=f'info_{beer_id}_variations')],
                   [InlineKeyboardButton('Ingredients', callback_data=f'info_{beer_id}_ingredients')],
                   [InlineKeyboardButton('Adjuncts', callback_data=f'info_{beer_id}_adjuncts')]]
        reply_markup = InlineKeyboardMarkup(options)
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Want to know more?",
                                 reply_markup=reply_markup)

    @send_typing_action
    def _show_options(self, beers, update: Updater, context: CallbackContext):
        beer_options = [InlineKeyboardButton(beer.get('name', ''), callback_data=f'beer_{beer.get("id")}') for beer in
                        beers]
        reply_markup = InlineKeyboardMarkup(build_menu(beer_options, n_cols=3))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your destiny 💀",
                                 reply_markup=reply_markup)

    @send_typing_action
    def _select_beer(self, update: Updater, context: CallbackContext):
        query = update.callback_query
        beer_id = query.data.replace('beer_', '')
        try:
            beer = self._client.get_by_id(beer_id)
            self._send_beer(beer, update, context)
        except HTTPError:
            self._not_found(update, context)

    @send_typing_action
    def _select_info(self, update: Updater, context: CallbackContext):
        query = update.callback_query
        [prefix, beer_id, command_name] = query.data.split('_')
        client_mapping = {
            'variations': self._client.get_variations,
            'ingredients': self._client.get_ingredients,
            'adjuncts': self._client.get_adjuncts,
        }
        parse_mapping = {
            'variations': self._parse_variations,
            'ingredients': self._parse_ingredients,
            'adjuncts': self._parse_adjuncts,
        }

        try:
            result = client_mapping[command_name](beer_id)
            text = parse_mapping[command_name](result)
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        except KeyError:
            self._not_found(update, context)

    def handle_error(self, update, context):
        if update.effective_message:
            text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
                   "My developer(s) will be notified."
            update.effective_message.reply_text(text)

        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        payload = ""
        if update.effective_user:
            payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'

        if update.effective_chat:
            payload += f' within the chat <i>{update.effective_chat.title}</i>'
            if update.effective_chat.username:
                payload += f' (@{update.effective_chat.username})'

        if update.poll:
            payload += f' with the poll id {update.poll.id}.'

        text = f"The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
               f"</code>"

        for dev_id in Devs:
            context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)

        raise

    def _parse_variations(self, variations):
        pass

    def _parse_ingredients(self, variations):
        pass

    def _parse_adjuncts(self, variations):
        pass

    def _parse_beer_to_html(self, raw_beer):
        name = raw_beer.get('name', 'Not Found')
        abv = raw_beer['abv']
        ibu = raw_beer['ibu']
        style = raw_beer['style']
        category = raw_beer['category']
        desc = raw_beer['description']
        breweries = raw_beer['breweries']
        accounts = raw_beer['accounts']

        text = f'🍺🍺🍺 <b>"{name}"</b> 🍺🍺🍺\n' \
               f'\n📈 <i>ABV={abv}\n📉 IBU={ibu}</i> \n' \
               f'\n️💅 <b>Style</b>:\n{style}\n' \
               f'\n🗃️ <b>Category</b>:\n{category}\n' \
               f'\n️✍️ <b>Description</b>:\n{desc}\n'

        if breweries:
            breweries_text = ''
            for b in breweries:
                breweries_text = f'{breweries_text}{b["name"]}\n'
            text += f'\n️🏠 <b>Breweries</b>:\n{breweries_text}\n'

        if accounts:
            accounts_text = ''
            for b in accounts:
                accounts_text = f'{accounts_text}{b["name"]} {b["link"]}\n'
            text += f'\n️💁‍♂️ <b>More Info</b>:\n{accounts_text}\n'

        return text