from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove, Update

from app import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TelegramToken = ''

updater = Updater(token=TelegramToken, use_context=True)
dispatcher = updater.dispatcher
queue = updater.job_queue


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text='Hello, welcome!')


def option(update, context):
    button = [
        [InlineKeyboardButton("Option 1", callback_data='1'),
         InlineKeyboardButton("Option 2", callback_data='2')],
    ]
    reply_markup = InlineKeyboardMarkup(button)
    context.bot.send_message(chat_id=update.message.chat_id, text='Choose one option', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  text="Thanks for choosing {}.".format(query.data),
                                  message_id=query.message.message_id)


def get_location(update, context):
    button = [
        [KeyboardButton(text="Send location", request_location=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(button)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Mind sharing location?",
                             reply_markup=reply_markup)


def location(update, context):
    logging.log(update.message.location)
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Longitude: {}, Latitude: {}".format(lon, lat),
                             reply_markup=ReplyKeyboardRemove())


def callback_alarm(context: CallbackContext):
    context.bot.send_message(chat_id=context.job.context, text='BEEP')


def callback_timer(update: Update, context: CallbackContext):
    delay = context.args[0]
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=f'Setting a timer for {delay} seconds!')

    context.job_queue.run_once(callback_alarm, delay, context=update.message.chat_id)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


start_handler = CommandHandler('start', start)
option_handler = CommandHandler('option', option)
button_handler = CallbackQueryHandler(button)
get_location_handler = CommandHandler('location', get_location)
location_handler = MessageHandler(Filters.location, location, pass_user_data=True)
timer_handler = CommandHandler('timer', callback_timer)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(option_handler)
dispatcher.add_handler(button_handler)
dispatcher.add_handler(get_location_handler)
dispatcher.add_handler(location_handler)
dispatcher.add_handler(timer_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
