from __future__ import annotations

import collections
from datetime import datetime
from typing import List, Tuple, TYPE_CHECKING

import discord
import discordSuperUtils
import pikudhaoref
from discord.ext import commands

from ..core.bot import SirenBot
from ..converters import DatetimeConverter

if TYPE_CHECKING:
    from pikudhaoref.siren import Siren


class Sirens(commands.Cog):
    """
    Represents a sirens cog
    """

    def __init__(self, bot: SirenBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.client.add_event(self.on_siren)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setsiren(self, ctx, channel: discord.TextChannel = None):
        channel = channel if channel is not None else ctx.channel

        assert self.bot.database, "The database has not been connected yet."
        await self.bot.database.updateorinsert(
            "siren_channels",
            {"siren_channel": channel.id},
            {"guild": ctx.guild.id},
            {"guild": ctx.guild.id, "siren_channel": channel.id},
        )

        embed = discord.Embed(
            title="Success!",
            description=f"Set siren alert channel to {channel.mention}.",
            color=0x00FF00,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def help(self, ctx):
        prefix = self.bot.command_prefix
        embed = discord.Embed(
            title="List of commands | SirenBot",
            description="List of usable commands.",
            color=0xFF0000,
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(
            name=f"ℹ️ {prefix}help",
            value="Shows a list of usable commands.",
            inline=False,
        )

        embed.add_field(
            name=f"🚨 {prefix}setsiren [channel]",
            value="Assigns the siren log to the specified channel.",
            inline=False,
        )

        embed.add_field(
            name=f"🧪 {prefix}testsiren",
            value="Sends a test siren alert to the siren log assigned channel.",
            inline=False,
        )

        embed.add_field(
            name=f"📜 {prefix}history <day/week/month/range> [start] [end]",
            value="Shows the siren history.",
            inline=False,
        )

        embed.add_field(
            name=f"⚙️ {prefix}settings",
            value="Shows a list of the current server's settings.",
            inline=False,
        )

        embed.add_field(
            name=f"ℹ️ {prefix}info",
            value="Shows information about SirenBot and siren activity.",
            inline=False,
        )

        embed.add_field(
            name=f"🏙️ {prefix}cities [add/remove]",
            value="Add/remove a city.\nNote: These cities are keyword based.",
            inline=False,
        )

        embed.add_field(
            name=f"🚨 {prefix}zones [add/remove]",
            value="Add/remove a zone.",
            inline=False,
        )

        await ctx.send(embed=embed)

    @staticmethod
    def _get_city_name(city: pikudhaoref.City | str) -> str:
        return city if isinstance(city, str) else city.name.en

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title="Status | SirenBot",
            description="Shows information about SirenBot and siren activity.",
            color=0xFF0000,
        )

        siren_history = await self.bot.client.get_history(
            mode=pikudhaoref.HistoryMode.LAST_MONTH
        )

        common_city_text = last_siren_text = "There were no sirens in the last month."

        if siren_history:
            common_city = collections.Counter(
                [x.city for x in siren_history]
            ).most_common()[0]
            last_siren_in_common = next(
                (x for x in siren_history if x.city == common_city[0]), None
            )
            last_siren = siren_history[0]

            last_siren_text = f"**Date:** {last_siren.datetime}, **Location:** {self._get_city_name(last_siren.city)}"

            if common_city and last_siren_in_common:
                common_city_text = f"**Location:** {self._get_city_name(last_siren_in_common.city)}, **Last Siren:** {last_siren_in_common.datetime}, **Number of Sirens:** {common_city[1]}"

        uptime = datetime.fromtimestamp(self.bot.start_time).strftime(
            "%Y-%m-%d, %H:%M:%S"
        )

        embed.add_field(
            name="⏲ SirenBot Uptime",
            value=f"**SirenBot Has Been Up Since:** {uptime}",
            inline=False,
        )

        embed.add_field(
            name="🚨 Last Siren (last month)", value=last_siren_text, inline=False
        )

        embed.add_field(
            name="📜 City With the Most Sirens (last month)",
            value=common_city_text,
            inline=False,
        )

        embed.add_field(
            name="🚀 Number of Sirens (last month)",
            value=str(len(siren_history)),
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def testsiren(self, ctx):
        embed = discord.Embed(
            title="Test Siren!",
            description=f"This is a test siren alert called by {ctx.author.mention}.",
            color=0xFF0000,
        )

        siren_channel_record = await self.bot.database.select(
            "siren_channels", ["siren_channel"], {"guild": ctx.guild.id}
        )
        if not siren_channel_record:
            await ctx.send(
                "You have not assigned the siren log to a channel! "
                "assign it to a channel using the ?setsiren command."
            )
            return

        channel_id = siren_channel_record["siren_channel"]

        channel = ctx.guild.get_channel(int(channel_id))
        if channel is not None:
            message = await channel.send(embed=embed)

            await message.add_reaction("🟥")
        else:
            raise commands.BadArgument("The siren log assigned channel is not found.")

    async def _get_guild_settings(
        self, guild: discord.Guild
    ) -> Tuple[discord.TextChannel, List[str], List[str]]:
        siren_record = await self.bot.database.select(
            "siren_channels", ["siren_channel"], {"guild": guild.id}
        )

        if not siren_record:
            channel = None
        else:
            channel_id = siren_record["siren_channel"]
            channel = guild.get_channel(channel_id)

        city_records = await self.bot.database.select(
            "cities", ["city"], {"guild": guild.id}, fetchall=True
        )
        zone_records = await self.bot.database.select(
            "zones", ["zone"], {"guild": guild.id}, fetchall=True
        )

        return (
            channel,
            [city_record["city"] for city_record in city_records],
            [zone_record["zone"] for zone_record in zone_records],
        )

    @staticmethod
    def _check_city_whitelisted(
        city: pikudhaoref.City | str, cities: List[str], zones: List[str]
    ) -> bool:
        if isinstance(city, str):
            siren_city_names = [city]
            siren_zone_names = []
        else:
            siren_city_names = city.name.languages
            siren_zone_names = [x.casefold() for x in city.zone.languages]

        return any(
            any(city.casefold() in siren_city.casefold() for city in cities)
            for siren_city in siren_city_names
        ) or any((zone.casefold() in siren_zone_names for zone in zones))

    @staticmethod
    def _format_city(city: pikudhaoref.City | str) -> str:
        return (
            f"City: {city}, Zone: Unknown, Countdown: Unknown"
            if isinstance(city, str)
            else f"City: {city.name.en}, Zone: {city.zone.en}, Countdown: {city.countdown.seconds}"
        )

    async def on_siren(self, sirens: List[Siren]):
        if not self.bot.database:
            return

        sirens = self.sort_sirens(sirens)

        for guild in self.bot.guilds:
            channel, cities, zones = await self._get_guild_settings(guild)

            if not channel:
                continue

            result_sirens = []
            for siren in sirens:
                if cities or zones:
                    if not self._check_city_whitelisted(siren.city, cities, zones):
                        continue

                result_sirens.append(siren)

            if not result_sirens:
                continue

            sirens_formatted = "\n".join(
                [self._format_city(x.city) for x in result_sirens]
            )

            message = await channel.send(
                embed=discord.Embed(
                    title="Siren Alert!",
                    description=f"**Locations:**\n {sirens_formatted}",
                    color=0xFF0000,
                ).add_field(
                    name="Common Zones",
                    value=", ".join(x[0] for x in self.get_common_zones(result_sirens)),
                )
            )

            await message.add_reaction("🟥")

    @staticmethod
    def get_common_zones(sirens: List[Siren]) -> List[Tuple[str, int]]:
        return collections.Counter(
            [x.city.zone.en for x in sirens if isinstance(x.city, pikudhaoref.City)]
        ).most_common(5)

    @staticmethod
    def sort_sirens(sirens: List[Siren]) -> List[Siren]:
        return sorted(sirens, key=lambda x: x.city.countdown.seconds)

    def _create_siren_paginator(
        self,
        ctx: commands.Context,
        sirens: List[Siren],
        siren_mode: pikudhaoref.HistoryMode,
    ) -> discordSuperUtils.PageManager:
        formatted_list = []
        for siren in sirens:
            city = self._get_city_name(self.bot.client.get_city(siren.city))
            formatted_list.append(f"Location: {city}, Date: {siren.datetime} UTC")

        return discordSuperUtils.PageManager(
            ctx,
            discordSuperUtils.generate_embeds(
                formatted_list, "Siren History", f"Siren History mode {siren_mode}"
            ),
        )

    @commands.group(invoke_without_command=True)
    async def history(self, ctx, mode: str):
        modes = {
            "day": pikudhaoref.HistoryMode.TODAY,
            "week": pikudhaoref.HistoryMode.LAST_WEEK,
            "month": pikudhaoref.HistoryMode.LAST_MONTH,
        }

        siren_mode = modes.get(mode.lower())
        if not siren_mode:
            await ctx.send(f"mode '{mode}' is not found.")
            return

        await self._create_siren_paginator(
            ctx, await self.bot.client.get_history(mode=siren_mode), siren_mode
        ).run()

    @history.command()
    async def range(self, ctx, from_: DatetimeConverter, to_: DatetimeConverter = None):
        async with ctx.typing():  # This might take a while.
            to_ = to_ or datetime.utcnow()

            siren_mode = pikudhaoref.HistoryMode.RANGE

            assert isinstance(from_, datetime)

            paginator = self._create_siren_paginator(
                ctx,
                await self.bot.client.get_history(range_=pikudhaoref.Range(from_, to_)),
                siren_mode,
            )

        await paginator.run()


def setup(bot: SirenBot):
    bot.add_cog(Sirens(bot))
