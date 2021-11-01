from datetime import datetime

from discord.ext import commands


class DatetimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return datetime.strptime(argument, "%Y-%m-%d")
        except ValueError:
            raise commands.BadArgument(f"'{argument}' must match format %Y-%m-%d.")
