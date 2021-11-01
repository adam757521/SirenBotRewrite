import discord
import discordSuperUtils
from discord.ext import commands

from bot import SirenBot


class Customization(commands.Cog):
    def __init__(self, bot: SirenBot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def cities(self, ctx):
        city_records = await self.bot.database.select(
            "cities", ["city"], {"guild": ctx.guild.id}, fetchall=True
        )

        cities = [city_record["city"] for city_record in city_records]
        await discordSuperUtils.PageManager(
            ctx,
            discordSuperUtils.generate_embeds(
                cities,
                "List of cities",
                f"Shows the list of the custom cities in {ctx.guild}",
                string_format="City: '{}'",
            ),
        ).run()

    @cities.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add_(self, ctx, city_name: str):
        await self.bot.database.insertifnotexists(
            "cities",
            {"guild": ctx.guild.id, "city": city_name},
            {"guild": ctx.guild.id, "city": city_name},
        )
        await ctx.send(f"City '{city_name}' has been added.")

    @cities.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove_(self, ctx, city_name: str):
        await self.bot.database.delete(
            "cities", {"guild": ctx.guild.id, "city": city_name}
        )
        await ctx.send(f"City '{city_name}' has been removed from the city list.")

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def zones(self, ctx):
        zone_records = await self.bot.database.select(
            "zones", ["zone"], {"guild": ctx.guild.id}, fetchall=True
        )

        cities = [zone_record["city"] for zone_record in zone_records]
        await discordSuperUtils.PageManager(
            ctx,
            discordSuperUtils.generate_embeds(
                cities,
                "List of zones",
                f"Shows the list of the custom zones in {ctx.guild}",
                string_format="Zone: '{}'",
            ),
        ).run()

    @zones.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, zone_name: str):
        await self.bot.database.insertifnotexists(
            "zones",
            {"guild": ctx.guild.id, "zone": zone_name},
            {"guild": ctx.guild.id, "zone": zone_name},
        )
        await ctx.send(f"Zone '{zone_name}' has been added.")

    @zones.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, zone_name: str):
        await self.bot.database.delete(
            "zones", {"guild": ctx.guild.id, "zone": zone_name}
        )
        await ctx.send(f"Zone '{zone_name}' has been removed from the zone list.")

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


def setup(bot: SirenBot):
    bot.add_cog(Customization(bot))
