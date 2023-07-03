from apps.profiles.models import User, tg_key_gen
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def start(update, context):
    existing = User.objects.filter(tg_chat_id=update.message.chat_id).exclude(
        tg_chat_id=""
    )
    if existing:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Welcome back! Your messages from Artconomy for "
            f"{existing[0].username} will continue now.",
        )
        return
    if not context.args:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm missing your key. Please add your Telegram via your account "
            "settings to start this process.",
        )
        return
    args = context.args[0].rsplit("_")
    if len(args) != 2:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me appears to be corrupt. Please add your telegram "
            "via your account settings to send a starting message with your key.",
        )
        return
    try:
        user = User.objects.get(username=args[0], tg_key=args[1])
    except User.DoesNotExist:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me does not appear to match any account. Please add "
            "your telegram via your account settings to send a starting message "
            "with your key.",
        )
        return
    user.tg_chat_id = update.message.chat_id
    user.tg_key = tg_key_gen()
    user.save()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Hi! I'm the Artconomy bot. I'll send messages for {user.username}'s Two "
        f"Factor Authentication codes. Please visit the site for more information.",
    )


def help_message(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Sorry, I didn't understand that. If you're having trouble, please "
        "contact support@artconomy.com.",
    )


start_handler = CommandHandler("start", start)
help_handler = MessageHandler(Filters.text, help_message)
unknown_handler = MessageHandler(Filters.command, help_message)


def init(api_key):
    updater = Updater(token=api_key, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(unknown_handler)
    return updater
