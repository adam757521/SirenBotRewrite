from datetime import datetime

from discord.ext import commands


class DatetimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return datetime.strptime(argument, "%Y-%m-%d")
        except ValueError:
            raise commands.BadArgument(f"'{argument}' must match format %Y-%m-%d.")


class TableDataConverter(commands.Converter):
    TABLE_DICT = {
        "cities": ("cities", "city"),
        "zones": ("zones", "zone"),
    }

    async def convert(self, ctx, argument):
        if argument.lower() not in self.TABLE_DICT:
            raise commands.BadArgument(f"'{argument}' is not a valid table.")

        return self.TABLE_DICT.get(argument.lower())
