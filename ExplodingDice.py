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

    def locationFromNum(self, num) -> str:
        loc = ""
        if num < 5:
            loc = "Leg"
        elif num < 10:
            loc = "Lower Guts"
        elif num == 10:
            loc = "Gizzards"
        elif num < 15:
            loc = "Arm"
        elif num < 20:
            loc = "Upper Guts"
        else:
            loc = "Noggin"
        if loc == "Leg" or loc == "Arm":
            if num % 2 == 0:
                loc = "Right " + loc
            elif num % 2 == 1:
                loc = "Left " + loc
        return loc

    def rollLocation(self, raises, isBrawl=False):
        roll = random.randint(1, 20)
        if isBrawl:
            roll += 4
            if roll > 20:
                roll = 20
        msg = "Location: " + str(roll) + " " + self.locationFromNum(roll)
        if raises > 0:
            locs = set()
            msg += "\nCan be moved to:"
            for n in range(roll - raises, roll + raises + 1):
                if n != roll:
                    locs.add(self.locationFromNum(n))
            for l in locs:
                if l != self.locationFromNum(roll):
                    msg += "\n" + l
        return msg

    @commands.command(
        brief="Rolls exploding dice and take the highest. Format: !roll <numDice>d<numSides>"
    )
    async def roll(self, ctx, idj):
        numDice, numSides = idj.split("d")
        numDice = int(numDice)
        numSides = int(numSides)
        val, vals = self.rollE(numDice, numSides)
        msg = ctx.author.global_name + " rolled " + str(val) + ", " + str(vals) + "."

        count = vals.count(1)
        isBust = False
        if numDice == 1 and count == 1:
            isBust = True
        elif numDice == 2 and count == 2:
            isBust = True
        elif numDice > 2 and count > (numDice / 2):
            isBust = True
        if isBust:
            msg += "\n" + ctx.author.global_name + " went bust!"

        await ctx.send(msg)

    @commands.command(
        brief="Rolls exploding dice and sums them. Format: !rollSum <numDice>d<numSides>"
    )
    async def rollSum(self, ctx, idj):
        numDice, numSides = idj.split("d")
        val = self.rollE(int(numDice), int(numSides), True)
        msg = ctx.author.global_name + " rolled " + str(val) + "."
        await ctx.send(msg)

    @commands.command(
        "rollHitLocation",
        brief="Opt: num raises, brawl. Rolls a hit location.",
        help=" num raises for where you can move it, any other argument after (so requires a raises num, even if zero) for a plus 4 for brawling.",
        aliases=["hitLocation"],
    )
    async def rollHitLocation(self, ctx, raises=0, isBrawling=""):
        if isBrawling == "":
            brawl = False
        else:
            brawl = True
        msg = self.rollLocation(int(raises), brawl)
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(ExplodingDice(bot))
