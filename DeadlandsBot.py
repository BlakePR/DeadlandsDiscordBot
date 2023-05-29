import asyncio, discord, dotenv
from discord.ext import commands
import ExplodingDice, Cards, Chips
import dotenv

TOKEN = dotenv.get_key(".env", "TOKEN")

Intents = discord.Intents.default()
Intents.message_content = True

bot = discord.ext.commands.Bot(command_prefix="!", intents=Intents)
bot.help_command = commands.MinimalHelpCommand()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


async def main():
    await Chips.setup(bot)
    await ExplodingDice.setup(bot)
    await Cards.setup(bot)
    await bot.start(TOKEN)


async def close(bot):
    await bot.close()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    cog1 = bot.get_cog("Chips")
    cog1.save()
    asyncio.run(close(bot))
