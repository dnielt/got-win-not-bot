import config
import logging
import re
from winnings import calculate_winnings
from gcloud_vision import read_image
from telegram import (
    ReplyKeyboardMarkup, 
    Update, 
    ReplyKeyboardRemove, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)

#token = os.environ['TELEGRAM_TOKEN']

CHOOSE_INPUT, DATE, MSG_TICKET_NUMBERS = range(3)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Hi! Welcome to daniel's toto winnings"
                             "calculator. Send me the ticket date, in the format" 
                             "<yyyy-mm-dd>.")
    return CHOOSE_INPUT

def choose_input(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Choose an input type.\n"
                             "1) Photo of toto slip.\n" 
                             "2) Text input.")
    keyboard = [
        [
            InlineKeyboardButton("1) Photo of toto slip", callback_data='1'),
            InlineKeyboardButton("2) Text input", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return DATE

def date(update, context):
    ticket_date = update.message.text
    logger.info(f"Received plain text: {ticket_date}")
    context.user_data["ticket_date"] = ticket_date
    update.message.reply_text(f"You entered: {ticket_date}.\n"
                              f"Now enter the ticket number(s) separated by space.\n"
                              f"Enter multiple tickets across multiple lines.")
    
    return MSG_TICKET_NUMBERS

def msg_ticket_numbers(update, context):
    """received as 1 2 3 4 5 6, 1 2 3 4 5 6"""
    ticket_numbers = update.message.text
    logger.info(f"Received plain text:\n{ticket_numbers}")
    if re.findall("\n", ticket_numbers):
        ticket_numbers = re.split("\n", ticket_numbers)
        ticket_numbers = [re.split(" ", i) for i in ticket_numbers]
    else:
        ticket_numbers = re.split(" ", ticket_numbers)
    # context.user_data["ticket_numbers"] = ticket_numbers
    if isinstance(ticket_numbers[0], list):
        final = [calculate_winnings(context.user_data["ticket_date"], i)
                 for i in ticket_numbers]
    else:
        final = [calculate_winnings(context.user_data["ticket_date"], ticket_numbers)]
    # winnings = calculate_winnings(context.user_data["ticket_date"], final)
    num_matches = [i[0] for i in final]
    final_group = [i[1] for i in final]
    update.message.reply_text(f"You entered:\n{ticket_numbers}\n"
                              f"You won {final_group}\n"
                              f"Numbers matched: (ordinary numbers, additional\n"
                              f"{num_matches}")
    return ConversationHandler.END


def done(update, context):
    update.message.reply_text("done")
    return ConversationHandler.END

def main():
    updater = Updater(token=config.token, use_context=True)
    # updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_INPUT: [MessageHandler(FIlters.text, choose_input)],
            DATE: [MessageHandler(Filters.text, date)],
            MSG_TICKET_NUMBERS: [MessageHandler(Filters.text, msg_ticket_numbers)]
            },
            fallbacks=[MessageHandler(Filters.text, done)],
        )
    
    dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()

