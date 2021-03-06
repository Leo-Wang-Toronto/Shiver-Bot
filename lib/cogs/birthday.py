from discord.ext.commands import Cog
from discord.ext.commands import command
from discord.ext.commands import has_permissions

from re import fullmatch
from datetime import datetime

from ..db import db


class Birthday(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="birthday", aliases=["bday"], brief="Adds birthday notification for the given user, date must be in "
                                                      "the form DD/MM/YYYY")
    @has_permissions(manage_roles=True)
    async def birthday(self, ctx, mention, date):
        mention = mention.strip()
        date = date.strip()
        if self.validate_birthday(mention, date):
            db.execute("INSERT OR REPLACE INTO birthdays(UserID, GuildID, date) VALUES (?, ?, ?)",
                       mention[3:len(mention) - 1], ctx.guild.id, date)
            await ctx.send(f"Added birthdate {date} for {mention}")
        else:
            await ctx.send("Invalid format! (Type /help for syntax)")

    @command(name="birthday_check", aliases=["bdaycheck"], brief="Checks birthdate for the given user in the form DD/MM/YYYY")
    async def birthday_check(self, ctx, mention):
        mention = mention.strip()
        record = db.record("SELECT * FROM birthdays WHERE UserID = ? AND GuildID = ?", mention[3:len(mention) - 1], ctx.guild.id)
        if record is None:
            await ctx.send("This this user has no recorded birthdate")
        else:
            await ctx.send(f"{mention}'s birthdate is on {record[2]}")

    @staticmethod
    def validate_birthday(mention, date):
        if (fullmatch("<@!\d{18}>", mention) is not None and fullmatch("\d\d/\d\d/\d\d\d\d", date) is not None
                and int(date[6:]) <= datetime.today().year):
            try:
                datetime(day=int(date[0:2]), month=int(date[3:5]), year=int(date[6:]))
            except ValueError:
                pass
            else:
                return True
        return False


def setup(bot):
    bot.add_cog(Birthday(bot))
