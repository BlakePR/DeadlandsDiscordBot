import discord
import random
from discord.ext import commands


class ExplodingDice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def rollE(self, numDice, numSides, is_sum=False):
        rolls = []
        for i in range(numDice):
            rollTotal = 0
            while True:
                roll = random.randint(1, numSides)
                rollTotal += roll
                if roll != numSides:
                    break
            rolls.append(rollTotal)
        if is_sum:
            return sum(rolls)
        else:
            return max(rolls), rolls

    @commands.command(
        brief="Rolls exploding dice and take the highest. Format: !roll <numDice>d<numSides>"
    )
    async def roll(self, ctx, idj):
        numDice, numSides = idj.split("d")
        val, vals = self.rollE(int(numDice), int(numSides))
        msg = ctx.author.name + " rolled " + str(val) + ", " + str(vals) + "."

        # count = vals.count(1)
        # isBust = False
        # if numDice == 1 and count == 1:
        #    isBust = True
        # if numDice == 2 and count == 2:
        #    isBust = True
        # if numDice > 2 and count > numDice / 2:
        #    isBust = True
        # if isBust:
        #    msg += "\n" + ctx.author.name + " went bust!"

        await ctx.send(msg)

    @commands.command(
        brief="Rolls exploding dice and sums them. Format: !rollSum <numDice>d<numSides>"
    )
    async def rollSum(self, ctx, idj):
        numDice, numSides = idj.split("d")
        val = self.rollE(int(numDice), int(numSides), True)
        msg = ctx.author.name + " rolled " + str(val) + "."
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(ExplodingDice(bot))
