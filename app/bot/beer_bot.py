from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from app.settings import TelegramToken


class BeerBot:
    def __init__(self, client):
        self._client = client
        self.updater = Updater(token=TelegramToken, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.random_handler = CommandHandler('random', self._random_beer)
        self.find_handler = CommandHandler('find', self._find_beer)
        self.select_handler = CallbackQueryHandler(self._select_option)
        self.unknown_handler = MessageHandler(Filters.command, self._unknown)

        self.dispatcher.add_handler(self.random_handler)
        self.dispatcher.add_handler(self.find_handler)
        self.dispatcher.add_handler(self.select_handler)
        self.dispatcher.add_handler(self.unknown_handler)

    def _unknown(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def _random_beer(self, update, context):
        beer = self._client.get_random()
        self._send_beer(beer, update, context)

    def _find_beer(self, update, context):
        user_message = update.message.text
        beer_name = user_message.replace('/find ', '')
        beers = self._client.find_by_name(beer_name)
        if len(beers) > 1:
            self._show_options(beers, update, context)
        else:
            self._send_beer(beers[0], update, context)

    def _send_beer(self, beer, update: Updater, context: CallbackContext):
        chat_id = update.effective_chat.id
        text = self._parse_beer_to_html(beer)
        context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
        context.bot.send_photo(chat_id=chat_id, photo=self._get_beer_image(beer))

    def _show_options(self, beers, update: Updater, context: CallbackContext):
        beer_options = [[InlineKeyboardButton(beer.get('name', ''), callback_data=beer.get('name')) for beer in beers]]
        reply_markup = InlineKeyboardMarkup(beer_options)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your destiny 💀",
                                 reply_markup=reply_markup)

    def _select_option(self, update: Updater, context: CallbackContext):
        query = update.callback_query
        beer = self._client.find_by_name(query.data)[0]
        self._send_beer(beer, update, context)

    def _parse_beer_to_html(self, raw_beer):
        name = raw_beer.get('name', 'Not Found')
        abv = raw_beer['abv']
        ibu = raw_beer['ibu']
        style = raw_beer['style']
        category = raw_beer['category']
        desc = raw_beer['description']
        text = f'🍺🍺🍺 <b>"{name}"</b> 🍺🍺🍺\n' \
               f'\n️💅 <b>Style</b>:\n{style}\n' \
               f'\n🗃️ <b>Category</b>:\n{category}\n' \
               f'\n️🍻 <b>Description</b>:\n{desc}\n' \
               f'\n📈 <i>ABV={abv}' \
               f'\n📉 IBU={ibu}</i>'
        return text

    def _get_beer_image(self, raw_beer):
        image_link = raw_beer['image_url']
        return image_link

    def run(self):
        self.updater.start_polling()
