import logging
import re
from winnings import calculate_winnings
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
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

DATE, MSG_TICKET_NUMBERS = range(2)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Hi! Welcome to daniel's toto winnings"
                             "calculator. Send me the ticket date, in the format" 
                             "<yyyy-mm-dd>.")
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
    updater = Updater(token="1724997205:AAHvk-UUDH9W1OR2xvktdpQ4VI7VRGRQa-o", 
                     use_context=True)
   # updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
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

