from asgiref.sync import sync_to_async

from apps.profiles.models import User, tg_key_gen
from telegram.ext import Application, CommandHandler, filters, MessageHandler


async def start(update, context):
    existing = await sync_to_async(
        User.objects.filter(tg_chat_id=update.message.chat_id)
        .exclude(tg_chat_id="")
        .first
    )()
    if existing:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Welcome back! Your messages from Artconomy for "
            f"{existing.username} will continue now.",
        )
        return
    if not context.args:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="I'm missing your key. Please add your Telegram via your account "
            "settings to start this process.",
        )
        return
    args = context.args[0].rsplit("_")
    if len(args) != 2:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me appears to be corrupt. Please add your telegram "
            "via your account settings to send a starting message with your key.",
        )
        return
    try:
        user = await sync_to_async(User.objects.get)(username=args[0], tg_key=args[1])
    except User.DoesNotExist:
        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text="The key you sent me does not appear to match any account. Please add "
            "your telegram via your account settings to send a starting message "
            "with your key.",
        )
        return
    user.tg_chat_id = update.message.chat_id
    user.tg_key = tg_key_gen()
    await sync_to_async(user.save)()
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Hi! I'm the Artconomy bot. I'll send messages for {user.username}'s Two "
        f"Factor Authentication codes. Please visit the site for more information.",
    )


async def help_message(update, context):
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Sorry, I didn't understand that. If you're having trouble, please "
        "contact support@artconomy.com.",
    )


start_handler = CommandHandler("start", start)
help_handler = MessageHandler(filters.TEXT, help_message)
unknown_handler = MessageHandler(filters.COMMAND, help_message)


def init(api_key):
    """
    Initializes the Telegram app. You must either use .initialize() or .run_polling()
    depending on your contextual needs in order for the bot to run/process updates.
    """
    application = Application.builder().token(api_key).build()
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(unknown_handler)
    return application
