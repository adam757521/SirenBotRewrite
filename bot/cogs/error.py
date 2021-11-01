from datetime import timedelta

import discord
import discordSuperUtils
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        discordSuperUtils.CommandHinter(bot)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time_to_wait = timedelta(seconds=round(error.retry_after))
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"You have to wait {time_to_wait} "
                    f"to use this command again.",
                    color=0xFF0000,
                )
            )

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(
                    embed=discord.Embed(
                        title="Error",
                        description="This command may only be executed in a guild.",
                        color=0xFF0000,
                    )
                )
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="This command may only be executed in a DM.",
                    color=0xFF0000,
                )
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"Please pass all the required arguments!",
                    color=0xFF0000,
                )
            )
            if ctx.command.is_on_cooldown(ctx):
                ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.BadArgument):
            try:
                await ctx.send(
                    embed=discord.Embed(
                        title="Error", description=str(error), color=0xFF0000
                    )
                )
                if ctx.command.is_on_cooldown(ctx):
                    ctx.command.reset_cooldown(ctx)
            except discord.HTTPException:
                pass  # same thing here

        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send(
                embed=discord.Embed(
                    title="Error",
                    description="This channel is SFW. (Safe For Work)",
                    color=0xFF0000,
                )
            )

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title="Permission Error.",
                    description="You don't have permission to use this command.",
                    color=0xFF0000,
                )
            )

        elif isinstance(error, commands.CommandInvokeError):
            if "Missing Permissions" in str(error):
                await ctx.send(
                    embed=discord.Embed(
                        title="Permission Error.",
                        description="I am missing permissions.",
                        color=0xFF0000,
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title="Error",
                        description="An error occurred while executing this command",
                        color=0xFF0000,
                    )
                )
                raise error

        else:
            if "The check functions" not in str(error):
                print("an unknown error has occurred: ")
                raise error


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
