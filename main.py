import config
import logging
import re
from winnings import calculate_winnings
from gcloud_vision import read_image, parse_raw_numbers
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

(CHOOSE_INPUT, PHOTO_UPLOAD, PHOTO_CHECK1, PHOTO_CHECK2, 
TEXT_INPUT1, TEXT_INPUT2, TEXT_CHECK1, RESULTS, REPEAT) = range(9)

DATE_PATTERN = "^(20[012][0-9])\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$"

def start(update, context):
    reply_keyboard = [["Photo of TOTO slip", "Text input"]]
    update.message.reply_text(
        "Hello! Welcome to the GOT-WIN-ANOT bot.\n"
        "How would you like to check your TOTO winnings?\n"
        "Enter /exit at any time to quit.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))    
    return CHOOSE_INPUT

def photo_upload(update, context):
    """User to upload photo"""
    user = update.message.from_user
    update.message.reply_text(
        "Please send me a photo of your TOTO slip!\n"
        "Or send /text if you decide to use text input instead.\n"
        "\nPlease note that this only works for System 6 tickets for now.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTO_CHECK1

def photo_check1(update, context):
    """
    Use OCR to retrieve text in photo.
    """
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("user_photo.jpg")
    image = read_image("user_photo.jpg")
    context.user_data['ticket_date'] = date = image['date']
    context.user_data['parsed'] = parsed = image['parsed']
    
    # logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg", test)
    update.message.reply_text(
        "Great! Now check to see if the draw date and numbers are accurate.\n"
        "Send /text if you want to input text instead.\n")
    update.message.reply_text(f"Draw date: {date}\n")
    update.message.reply_text(f"Numbers: {image['result']}\n")

    reply_keyboard = [["Next", "Re-send image"]]
    update.message.reply_text(f"Press next to see results, or re-send image.",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PHOTO_CHECK2

def photo_check2(update, context):
    """
    User to edit numbers if necessary.
    """
    ticket_numbers = context.user_data["parsed"]
    logger.info(f"Received plain text:\n{ticket_numbers}")
    ticket_numbers = parse_raw_numbers(ticket_numbers)
    if isinstance(ticket_numbers[0], list):
        final = [calculate_winnings(context.user_data["ticket_date"], i)
                 for i in ticket_numbers]
    else:
        final = [calculate_winnings(context.user_data["ticket_date"], ticket_numbers)]
    context.user_data["final"] = final
    reply_keyboard = [["Next"]]
    update.message.reply_text(f"You entered: {ticket_numbers}.\n"
                              f"Press next to see results.\n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RESULTS

def text_input1(update, context):
    update.message.reply_text(f"Enter the ticket date in the following format:\n"
                              f"yyyy-mm-dd")
    return TEXT_INPUT2
    
def text_input2(update, context):
    if re.match(DATE_PATTERN, update.message.text):
        context.user_data["ticket_date"] = update.message.text
    update.message.reply_text(f"You entered: {context.user_data['ticket_date']}.\n"
                              f"Now enter the ticket number(s) separated by space.\n"
                              f"Enter multiple tickets across multiple lines.")
    return TEXT_CHECK1

def text_check1(update, context):
    """"""
    ticket_numbers = update.message.text
    logger.info(f"\nReceived plain text:\n{ticket_numbers}")
    ticket_numbers = parse_raw_numbers(ticket_numbers)
    logger.info(f"\nParsed numbers:\n{ticket_numbers}")
    if isinstance(ticket_numbers[0], list):
        final = [calculate_winnings(context.user_data["ticket_date"], i)
                 for i in ticket_numbers]
    else:
        final = [calculate_winnings(context.user_data["ticket_date"], ticket_numbers)]
    context.user_data["final"] = final
    reply_keyboard = [["Next", "Re-enter numbers"]]
    update.message.reply_text(f"You entered: {ticket_numbers}.\n"
                              f"Press next to see results, or re-enter numbers.\n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return RESULTS

def results(update, context):
    """
    Return winnings.
    """
    final = context.user_data["final"]
    num_matches = [i[0] for i in final]
    final_group = [i[1] for i in final]
    update.message.reply_text(f"You won Group:{final_group}\n"
                              f"Numbers matched: (ordinary numbers, additional)\n"
                              f"{num_matches}\n"
                              f"Type /start to restart.")
    return ConversationHandler.END

def exit(update, context):
    update.message.reply_text("exit")
    return ConversationHandler.END

def main():
    updater = Updater(token=config.token, use_context=True)
    # updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_INPUT: [
                MessageHandler(Filters.regex("^Photo"), photo_upload),
                MessageHandler(Filters.regex("^Text"), text_input1),
                CommandHandler("exit", exit)],
            PHOTO_CHECK1: [
                MessageHandler(Filters.photo, photo_check1), 
                CommandHandler("text", text_input1),
                CommandHandler("exit", exit)],
            PHOTO_CHECK2: [
                MessageHandler(Filters.regex("^Next"), photo_check2),
                MessageHandler(Filters.regex("^Re-send"), photo_upload),
                CommandHandler("exit", exit)],
            TEXT_INPUT1: [
                MessageHandler(Filters.text, text_input1),
                CommandHandler("exit", exit)],
            TEXT_INPUT2: [
                #Regular expression to detect yyyy-mm-dd pattern
                MessageHandler(Filters.regex(DATE_PATTERN), text_input2),
                CommandHandler("exit", exit),
                #If any other input, re-enter date
                MessageHandler(Filters.text, text_input1)],
            TEXT_CHECK1: [
                CommandHandler("exit", exit),
                #Regular expression to detect xx xx xx xx xx xx\n pattern
                MessageHandler(Filters.regex(
                    "^([0][1-9]|[1-4][0-9])(( )([0][1-9]|[1-4][0-9])($|\n)*){5,}"), text_check1),
                #If any other input, re-enter date
                # MessageHandler(Filters.regex("[^0-9 \n]"),text_input2),
                MessageHandler(Filters.text, text_input2)],
            RESULTS: [
                MessageHandler(Filters.regex("^Next"), results),
                MessageHandler(Filters.regex("^Re-enter"), text_input1),
                CommandHandler("exit", exit)]
            },
            fallbacks=[MessageHandler(Filters.text, exit)],
        )
    
    dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()

