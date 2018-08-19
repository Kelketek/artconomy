from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from apps.profiles.models import User, tg_key_gen


def start(bot, update, args):
    existing = User.objects.filter(tg_chat_id=update.message.chat_id).exclude(tg_chat_id='')
    if existing:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Welcome back! Your messages from Artconomy for {} will continue now.".format(existing[0].username)
        )
        return
    if not args:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm missing your key. Please click the link on your Artconomy "
                 "Portrait tab in your settings to send a starting message with your key."
        )
        return
    args = args[0].rsplit('_')
    if len(args) != 2:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me appears to be corrupt. Please click the link on your Artconomy "
                 "Portrait tab in your settings to send a starting message with your key."
        )
        return
    try:
        user = User.objects.get(username__iexact=args[0], tg_key=args[1])
    except User.DoesNotExist:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me does not appear to match any account. Please click the link on your Artconomy "
                 "Portrait tab in your settings to send a starting message with your key."
        )
        return
    user.tg_chat_id = update.message.chat_id
    user.tg_key = tg_key_gen()
    user.save()
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hi! I'm the Artconomy bot. I'll send messages for {}'s watchlist when artists become "
             "available if they're subscribing to our Portrait service, or I can send Two Factor Authentication "
             "codes. Please visit the site for more information.".format(user.username)
    )


def help_message(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Sorry, I didn't understand that. If you're having trouble, please contact support@artconomy.com."
    )


start_handler = CommandHandler('start', start, pass_args=True)
help_handler = MessageHandler(Filters.text, help_message)
unknown_handler = MessageHandler(Filters.command, help_message)


def init(api_key):
    updater = Updater(token=api_key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)
    return updater
