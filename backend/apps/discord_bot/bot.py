import interactions
from apps.lib.consumers import aprint
from django.conf import settings

bot = interactions.Client(token=settings.DISCORD_BOT_KEY)


@bot.command(
    name="my_first_command",
    description="This is the first command I made!",
    scope=settings.DISCORD_GUILD_ID,
)
async def my_first_command(ctx: interactions.CommandContext):
    await ctx.send("Hi there!")


@bot.event
async def on_guild_member_add(*args, **kwargs):
    await aprint(args)
    await aprint(kwargs)
