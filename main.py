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

(CHOOSE_INPUT, PHOTO_UPLOAD, PHOTO_CHECK1, PHOTO_CHECK2, 
TEXT_INPUT1, TEXT_INPUT2, TEXT_CHECK1, RESULTS, REPEAT) = range(9)

def start(update, context):
    reply_keyboard = [['Image of TOTO slip'], ['Text input']]
    update.message.reply_text(
        "Hello! Welcome to the GOT-WIN-ANOT bot."
        "How would you like to check your TOTO winnings?\n",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))    
    return CHOOSE_INPUT

def photo_upload(update, context):
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    update.message.reply_text(
        "Please send me a photo of your TOTO slip!"
        "Or send /text if you decide to use text input instead.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTO_CHECK1

def photo_check1(update, context):
    """
    To-do:
    Use read_image() function to read uploaded photo.
    Store draw date and draw numbers in context.
    Return the draw date for user to edit, or press Y to confrim.
    
    Update draw date using user input if required.
    
    <yyyy-mm-dd>
    
    Send user to photo_check2.
    """
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    update.message.reply_text(
        "Great! Now check to see if the draw date and numbers are accurate.\n"
        "Send /text if you want to input text instead.")
    return PHOTO_CHECK2

def photo_check2(update, context):
    """
    To-do:
    Return draw numbers from context for user to edit, or press Y to confirm.
    
    Update draw numbers using user input if required.
    
    Enter the ticket number(s) separated by space.
    Enter multiple tickets across multiple lines.
    
    Send user to results.
    """
    return RESULTS

def text_input1(update, context):
    update.message.reply_text(f"Enter the ticket date in the following format:\n"
                              f"yyyy-mm-dd")
    return TEXT_INPUT2
    
def text_input2(update, context):
    context.user_data["ticket_date"] = update.message.text
    update.message.reply_text(f"You entered: {update.message.text}.\n"
                              f"Now enter the ticket number(s) separated by space.\n"
                              f"Enter multiple tickets across multiple lines.")
    return TEXT_CHECK1

def text_check1(update, context):
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
    context.user_data["final"] = final
    update.message.reply_text(f"You entered: {ticket_numbers}.\n"
                              f"Send any key to continue.")    
    return RESULTS

def results(update, context):
    """
    To-do:
    Pull draw date, draw numbers from context.
    Check against data.
    
    Return winnings.
    """
    final = context.user_data["final"]
    num_matches = [i[0] for i in final]
    final_group = [i[1] for i in final]
    context.bot.send_message(chat_id = update.effective_chat.id,
                             text= f"You won {final_group}\n"
                             f"Numbers matched: (ordinary numbers, additional)\n"
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
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_INPUT: [
                MessageHandler(Filters.regex("^Image"), photo_upload),
                MessageHandler(Filters.regex("^Text"), text_input1)],
            PHOTO_CHECK1: [
                MessageHandler(Filters.photo, photo_check1), 
                CommandHandler("text", text_input1)],
            PHOTO_CHECK2: [
                MessageHandler(Filters.text, photo_check2),
                CommandHandler("text", text_input1)],
            TEXT_INPUT1: [
                MessageHandler(Filters.text, text_input1)],
            TEXT_INPUT2: [
                MessageHandler(Filters.text, text_input2)],
            TEXT_CHECK1: [
                MessageHandler(Filters.text, text_check1)],
            RESULTS: [
                MessageHandler(Filters.text, results)]
            },
            fallbacks=[MessageHandler(Filters.text, done)],
        )
    
    dispatcher.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()

