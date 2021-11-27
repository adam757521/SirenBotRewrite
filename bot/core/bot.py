import time

import aiosqlite
import discordSuperUtils
import pikudhaoref

__all__ = ("SirenBot",)


class SirenBot(discordSuperUtils.DatabaseClient):
    """
    Represents the core SirenBot.
    """

    __slots__ = ("database", "start_time")

    def __init__(self, token: str, *args, **kwargs):
        super().__init__(token, *args, **kwargs)

        self.client = pikudhaoref.AsyncClient(update_interval=2, loop=self.loop)

        self.start_time = time.time()

    async def on_ready(self):
        print(f"{self.user} is ready.")

        await self.client.initialize()

        self.database = discordSuperUtils.DatabaseManager.connect(
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
