import discord

import bot


def main():
    bot.SirenBot(
        bot.Account.TOKEN,
        command_prefix=bot.Bot.PREFIX,
        intents=discord.Intents.all(),
        help_command=None,
    ).run(cogs_directory="bot/cogs")


if __name__ == "__main__":
    main()
