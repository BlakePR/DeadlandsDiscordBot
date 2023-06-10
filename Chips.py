import discord.ext.commands as commands
import json, random

defaultChips = {"black": 0, "blue": 10, "red": 25, "white": 50}


class Chips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chips = defaultChips if self.load()[0] is None else self.load()[0]
        self.playerChips = self.load()[1]

    def save(self):
        with open("chips.json", "w") as f:
            json.dump(self.chips, f)
        with open("players.json", "w") as f:
            json.dump(self.playerChips, f)

    def load(self):
        try:
            with open("chips.json", "r") as f:
                loadedChips = json.load(f)
        except:
            loadedChips = None
        try:
            with open("players.json", "r") as f:
                playerChips = json.load(f)
        except:
            playerChips = {}
        return loadedChips, playerChips

    def make_list(self):
        chipList = []
        for color, num in self.chips.items():
            for i in range(num):
                chipList.append(color)
        return chipList

    def pick3(self):
        chipList = self.make_list()
        return random.sample(chipList, 3)

    def remove(self, color):
        self.chips[color] -= 1

    def add(self, color):
        self.chips[color] += 1

    def addToPlayer(self, player, color):
        if self.playerChips.get(player, None) is None:
            self.playerChips[player] = {}
        self.playerChips[player][color] = self.playerChips[player].get(color, 0) + 1

    def removeFromPlayer(self, player, color) -> bool:
        if self.playerChips.get(player, None) is None:
            return False
        if self.playerChips[player].get(color, 0) == 0:
            return False
        self.playerChips[player][color] -= 1
        return True

    def list2str(self, chipList):
        chipDict = {}
        for color in chipList:
            chipDict[color] = chipDict.get(color, 0) + 1
        chipStr = ""
        for color, num in chipDict.items():
            chipStr += str(num) + " " + color + " chips, "
        chipStr = chipStr[:-2]
        return chipStr

    def dict2str(self, chipDict):
        msg = ""
        for color in chipDict.keys():
            msg += " " + str(chipDict.get(color, 0)) + " " + color + ","
        msg = msg[:-1]
        return msg

    @commands.command(name="getChips", brief="Get 3 random chips.")
    async def get_chips(self, ctx):
        givenChips = self.pick3()
        for chip in givenChips:
            self.remove(chip)
            self.addToPlayer(ctx.author.name, chip)
        msg = ctx.author.name + " has been given " + self.list2str(givenChips) + "."
        await ctx.send(msg)

    # fix message to actually return
    @commands.command(
        name="getColor",
        brief="args: color, opt num, get num (def 1) chip of that color.",
    )
    async def get_color(self, ctx, color, num=1):
        for i in range(int(num)):
            self.remove(color.lower())
            self.addToPlayer(ctx.author.name, color.lower())
        msg = ctx.author.name + " has been given " + num + color + " chip"
        if num != 1:
            msg += "s"
        msg += "."
        await ctx.send(msg)

    @commands.command(
        name="getLegendary",
        brief="get legendary chip. can't be used with normal command, won't be added back to pot",
    )
    async def get_legendary(self, ctx):
        self.addToPlayer(ctx.author.name, "Legendary Black")
        msg = "Legendary black chip given."
        await ctx.send(msg)

    @commands.command(
        name="useLegendary", brief="use legendary chip, removes from player chips."
    )
    async def use_legendary(self, ctx):
        wasUsed = self.removeFromPlayer(ctx, "Legendary Black")
        if wasUsed:
            msg = "Legendary black chip used."
        else:
            msg = "You don't have a legendary black chip."
        await ctx.send(msg)

    @commands.command(name="getRandom", brief="get a random chip.")
    async def get_random(self, ctx):
        givenChip = random.choice(self.make_list())
        self.remove(givenChip)
        self.addToPlayer(ctx.author.name, givenChip)
        msg = ctx.author.name.title() + " has been given a " + givenChip + " chip."
        await ctx.send(msg)

    @commands.command(
        name="returnChips",
        brief="args: num1 color1, opt: num2 color2, up to 4, return chips to pot.",
        aliases=["returnchips", "useChips", "use"],
    )
    async def return_chips(
        self,
        ctx,
        num1,
        color1,
        num2=None,
        color2=None,
        num3=None,
        color3=None,
        num4=None,
        color4=None,
    ):
        num1 = int(num1)
        isValid = True
        for i in range(num1):
            self.add(color1.lower())
            isValid = isValid and self.removeFromPlayer(ctx.author.name, color1.lower())
        if num2:
            num2 = int(num2)
            for i in range(num2):
                self.add(color2.lower())
                isValid = isValid and self.removeFromPlayer(
                    ctx.author.name, color2.lower()
                )
        if num3:
            num3 = int(num3)
            for i in range(num3):
                self.add(color3.lower())
                isValid = isValid and self.removeFromPlayer(
                    ctx.author.name, color3.lower()
                )
        if num4:
            num4 = int(num4)
            for i in range(num4):
                self.add(color4.lower())
                isValid = isValid and self.removeFromPlayer(
                    ctx.author.name, color4.lower()
                )
        if isValid:
            msg = "Chips returned."
        else:
            msg = "You don't have that many chips."
        await ctx.send(msg)

    @commands.command(name="addBlack", brief="add black chip to pot.")
    async def add_black(self, ctx):
        self.add("black")
        msg = "Black chip added."
        await ctx.send(msg)

    @commands.command(name="showChips", brief="Show current pot.")
    async def show_chips(self, ctx):
        msg = "Current pot: " + self.list2str(self.make_list()) + "."
        await ctx.send(msg)

    @commands.command(name="showMine", brief="Show your chips.")
    async def show_player_chips(self, ctx):
        msg = (
            ctx.author.name
            + "'s chips:"
            + self.dict2str(self.playerChips.get(ctx.author.name, {}))
            + "."
        )
        await ctx.send(msg)

    @commands.command(name="showAllPlayerChips", brief="Show everyone's chips.")
    async def show_all_player_chips(self, ctx):
        msg = ""
        for player in self.playerChips.keys():
            msg += (
                player
                + "'s chips: "
                + self.dict2str(self.playerChips.get(player, {}))
                + ".\n"
            )
        await ctx.send(msg)

    @commands.command(brief="save chips to file.")
    async def saveChips(self, ctx):
        self.save()
        msg = "Chips saved."
        await ctx.send(msg)

    @commands.command(brief="reset chips to default.")
    async def resetChips(self, ctx):
        self.chips = defaultChips
        self.playerChips = {}
        msg = "Chips reset."
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Chips(bot))
