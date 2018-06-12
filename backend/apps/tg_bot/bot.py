from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from apps.profiles.models import User, tg_key_gen


def start(bot, update, args):
    if User.objects.filter(tg_chat_id=update.message.chat_id).exclude(tg_chat_id='').exists():
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Welcome back! Your messages from Artconomy will continue now."
        )
        return
    if not args:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm missing your key. Please click the link on your Artconomy "
                 "Portrait tab in your settings to send a starting message with your key."
        )
        return
    args = args[0].split(':')
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
    user.tg_chat_id = '171085739'
    user.tg_key = tg_key_gen()
    user.save()
    bot.send_message(chat_id=update.message.chat_id, text="Welcome to the Artconomy bot!")


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


start_handler = CommandHandler('start', start, pass_args=True)
echo_handler = MessageHandler(Filters.text, echo)
unknown_handler = MessageHandler(Filters.command, unknown)


def init(api_key):
    updater = Updater(token=api_key)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(unknown_handler)
    return updater
