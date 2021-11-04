import discord
import discordSuperUtils
from discord.ext import commands

from bot import SirenBot
from bot.converters import TableDataConverter


class Customization(commands.Cog):
    def __init__(self, bot: SirenBot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def customization(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                title="Commands",
                description="Usable commands: (list|add|remove)",
                color=0xFF0000,
            )
        )

    @customization.command()
    @commands.guild_only()
    async def list(self, ctx, table_data: TableDataConverter):
        assert isinstance(table_data, tuple), "table_data is not a tuple"
        custom_list = await select_custom(table_data, self.bot.database, ctx.guild.id)

        await discordSuperUtils.PageManager(
            ctx,
            discordSuperUtils.generate_embeds(
                custom_list,
                f"List of {table_data[0]}",
                f"Shows the list of the custom {table_data[0]} in {ctx.guild}",
                string_format=f"{table_data[1]}: '" + "{}'",
            ),
        ).run()

    @customization.command()
    @commands.guild_only()
    async def add(self, ctx, table_data: TableDataConverter, *, value: str):
        assert isinstance(table_data, tuple), "table_data is not a tuple"

        await add_custom(table_data, self.bot.database, ctx.guild.id, value)
        await ctx.send(f"'{value}' has been added to the {table_data[1]} list.")

    @customization.command()
    @commands.guild_only()
    async def remove(self, ctx, table_data: TableDataConverter, *, value: str):
        assert isinstance(table_data, tuple), "table_data is not a tuple"

        await remove_custom(table_data, self.bot.database, ctx.guild.id, value)
        await ctx.send(f"'{value}' has been removed from the {table_data[1]} list.")

    @commands.command()
    @commands.guild_only()
    async def settings(self, ctx):
        prefix = self.bot.command_prefix

        information_record = await self.bot.database.select(
            "siren_channels", [], {"guild": ctx.guild.id}
        )

        channel_id = information_record["siren_channel"] if information_record else None

        embed = discord.Embed(
            title=f"{ctx.guild.name}'s Settings",
            description="List of the current server's settings.",
            color=0xFF0000,
        )

        embed.add_field(
            name="🚨 Siren Channel",
            value=f"<#{channel_id}>" if channel_id is not None else channel_id,
            inline=False,
        )
        embed.add_field(
            name="🏙️ Custom Cities", value=f"Use {prefix}cities", inline=False
        )
        embed.add_field(name="🚨 Custom Zones", value=f"Use {prefix}zones", inline=False)

        await ctx.send(embed=embed)


async def add_custom(
    table_data: tuple,
    database: discordSuperUtils.database.Database,
    guild_id: int,
    custom: str,
):
    await database.insertifnotexists(
        table_data[0],
        {"guild": guild_id, table_data[1]: custom},
        {"guild": guild_id, table_data[1]: custom},
    )


async def select_custom(
    table_data: tuple, database: discordSuperUtils.database.Database, guild_id: int
):
    records = await database.select(
        table_data[0], [table_data[1]], {"guild": guild_id}, fetchall=True
    )
    return [record[table_data[1]] for record in records]


async def remove_custom(
    table_data: tuple,
    database: discordSuperUtils.database.Database,
    guild_id: int,
    custom: str,
):
    await database.delete(table_data[0], {"guild": guild_id, table_data[1]: custom})


def setup(bot: SirenBot):
    bot.add_cog(Customization(bot))
