import logging
import os
import time
from typing import Optional

import aiosqlite
import discordSuperUtils
from discord.ext import commands
import pikudhaoref

__all__ = ("SirenBot",)


class SirenBot(commands.Bot):
    """
    Represents the core SirenBot.
    """

    __slots__ = ("token", "client", "database")

    def __init__(self, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.token = token
        self.client = pikudhaoref.AsyncClient(update_interval=2, loop=self.loop)

        self.start_time = time.time()
        self.database: Optional[discordSuperUtils.database.Database] = None

    async def on_ready(self):
        print(f"{self.user} is ready.")

        await self.client.initialize()

        self.database = discordSuperUtils.DatabaseManager.connect(  # Typehint in dsu.
            await aiosqlite.connect("main.sqlite")
        )
        await self.database.create_table(
            "siren_channels", {"guild": "INTEGER", "siren_channel": "INTEGER"}, True
        )
        await self.database.create_table(
            "cities",
            {
                "guild": "INTEGER",
                "city": "TEXT",
            },
            True,
        )
        await self.database.create_table(
            "zones",
            {
                "guild": "INTEGER",
                "zone": "TEXT",
            },
            True,
        )

        print("Pikudhaoref client is ready.")

    def load_cogs(self, directory: str) -> None:
        """
        Loads all the cogs in the directory.

        :param str directory: The directory to load.
        :return: None
        :rtype: None
        """

        extension_directory = directory.replace("/", ".")

        path = os.getcwd()
        slash = "/" if "/" in path else "\\"
        for file in os.listdir(path + f"{slash}{directory}"):
            if not file.endswith(".py") or file.startswith("__"):
                continue

            try:
                self.load_extension(f'{extension_directory}.{file.replace(".py", "")}')
                logging.info(f"Loaded cog {file}")
            except Exception as e:
                logging.critical(
                    f"An exception has been raised when loading cog {file}"
                )
                raise e

    def run(self) -> None:
        """
        Runs the bot.

        :return: None
        :rtype: None
        """

        self.load_cogs("bot/cogs")

        super().run(self.token)
