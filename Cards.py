from functools import total_ordering
import discord
import random
from discord.ext import commands

SUITS = ('♠', '♦', '♥', '♣')

@total_ordering
class Card():
    def __init__(self, suit, value, Joker=None):
        self.suit = suit
        self.value = value
        self.Joker = Joker
    
    def __str__(self):
        if self.Joker:
            return self.Joker + " Joker"
        return str(self.getValue()) + self.suit
    
    def getValue(self):
        if self.value == 14:
            return "A"
        elif self.value == 11:
            return "J"
        elif self.value == 12:
            return "Q"
        elif self.value == 13:
            return "K"
        else:
            return self.value
    
    def __lt__(self, other):
        if self.Joker:
            if other.Joker:
                return self.Joker < other.Joker
            return False
        if other.Joker:
            return True
        if self.value != other.value:
            return self.value < other.value
        else:
            #spade diamons Hearts clubs:
            return SUITS.index(self.suit) > SUITS.index(other.suit)
    
    def __eq__(self, other) -> bool:
        if self.Joker:
            return self.Joker == other.Joker
        return self.value == other.value and self.suit == other.suit
        
class Deck():
    def __init__(self):
        self.inDeck = []
        self.playersHands = {}
        self.cheated = {}
        self.discard = []
        self.buildDeck()
        
    def buildDeck(self):
        for suit in SUITS:
            for value in range(2, 15):
                self.inDeck.append(Card(suit, value))
        self.inDeck.append(Card(None, 0, "Red"))
        self.inDeck.append(Card(None, 1, "Black"))
        random.shuffle(self.inDeck)
    
    def shuffle(self):
        random.shuffle(self.inDeck)
        
    def shuffleIn(self):
        self.inDeck.extend(self.discard)
        self.discard = []
        self.shuffle()
    
    def printDeck(self):
        for card in self.inDeck:
            print(str(card))
    
    def getCard(self, player):
        card = self.inDeck.pop()
        if player not in self.playersHands:
            self.playersHands[player] = []
        self.playersHands[player].append(card)
        return card
    
    def getCards(self, player, num):
        cards = []
        for i in range(num):
            cards.append(self.getCard(player))
        return cards
            
    def stringPlayerHand(self, player):
        self.playersHands[player].sort()
        self.playersHands[player].reverse()
        msg = player + "'s hand:"
        for card in self.playersHands[player]:
            msg += str(card) + "\n"
        return msg
    
    def useCard(self, player, value):
        for i, card in enumerate(self.playersHands[player]):
            if card.value == value:
                self.discard.append(self.playersHands[player].pop(i))
                return True
        return False
    
    def cheatCard(self, player, value):
        for i, card in enumerate(self.playersHands[player]):
            if card.value == value:
                self.cheated[player] = self.playersHands[player].pop(i)
                return True
        return False
    
    def hasCheated(self, player):
        return player in self.cheated
    
    def useCheatedCard(self, player):
        if player in self.cheated:
            self.discard.append(self.cheated.pop(player))
            return True
        return False
    
    def getOrderedPlayerHands(self):
        order = []
        for player in self.playersHands:
            for card in self.playersHands[player]:
                order.append((player, card))
        order.sort(key=lambda x: x[1],reverse=True)
        return order
    
    def stringOrderPlayers(self):
        order = self.getOrderedPlayerHands()
        msg = ""
        prevPlayer = None
        for player, card in order:
            if prevPlayer != player:
                msg += "\n" + player + ": "
                prevPlayer = player
            msg += str(card) + " "
        return msg
    
    def flushPlayerHand(self, player):
        self.discard.extend(self.playersHands[player])
        self.playersHands[player] = []
    
    def flushAllHands(self):
        for player in self.playersHands.keys():
            self.flushPlayerHand(player)
            
    def checkBlackJoker(self,cards):
        for card in cards:
            if card.Joker == "Black":
                return True
        return False
    
    def blackJokerHandler(self,player):
        if self.checkBlackJoker(self.playersHands[player]):
            if self.hasCheated:
                self.useCheatedCard(player)
            self.useCard(player, 1)
            return True
        return False
        
class DeckManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deck = Deck()
        
    @commands.command(name="shuffle", brief="Shuffles deck, opt: shuffle discard into deck (any arg)")
    async def shuffle(self, ctx, discard=None):
        if discard:
            self.deck.shuffleIn()
        else:
            self.deck.shuffle()
        msg = "Shuffled"
        if discord:
            msg += " including discard pile in"
        await ctx.send(msg)
        
    @commands.command(name="getCards", brief="opt arg: num cards. Get(s) card(s) from the deck", aliases=["get"])
    async def getCards(self, ctx, num=1):
        msg = ""
        if num < 1:
            await ctx.send("Invalid number of cards")
            return
        cards = self.deck.getCards(ctx.author.name, num)
        bj = self.deck.blackJokerHandler(ctx.author.name)
        if bj:
            msg += "Got a black Joker, lost cheated card, remember to shuffle at end of round\n"
        msg += ctx.author.name + " got: "
        for card in cards:
            msg += str(card) + " "
        await ctx.send(msg)
        
    @commands.command(name="hand", brief="Prints your hand")
    async def hand(self, ctx):
        msg = self.deck.stringPlayerHand(ctx.author.name)
        if self.deck.hasCheated(ctx.author.name):
            msg += "\nCheated card: " + str(self.deck.cheated[ctx.author.name])
        await ctx.send(msg)
    
    @commands.command(name="useCard", brief="Use a card from your hand")
    async def useCard(self, ctx, value):
        if not self.deck.useCard(ctx.author.name, int(value)):
            await ctx.send("Invalid card")
            return
        await ctx.send("Used card")
    
    @commands.command(name="cheatCard", brief="Cheat a card from your hand", aliases = ["cheat"])
    async def cheatCard(self, ctx, value):
        if self.deck.hasCheated(ctx.author.name):
            await ctx.send("You have already cheated a card")
            return
        if not self.deck.cheatCard(ctx.author.name, int(value)):
            await ctx.send("Invalid card")
            return
        await ctx.send("Cheated card")
    
    @commands.command(name="useCheated", brief="Use the card you cheated")
    async def useCheated(self, ctx):
        if not self.deck.useCheatedCard(ctx.author.name):
            await ctx.send("You have not cheated a card")
            return
        await ctx.send("Used cheated card")
        
    @commands.command(name="emptyHand", brief="Discard your hand")
    async def emptyHand(self, ctx):
        self.deck.flushPlayerHand(ctx.author.name)
        await ctx.send("Emptied hand")
    
    @commands.command(name="emptyAllHands", brief="Discard all hands")
    async def emptyAllHands(self, ctx):
        self.deck.flushAllHands()
        await ctx.send("Emptied all hands")
    
    @commands.command(name="getOrder", brief="Get the initiative order")
    async def getOrder(self, ctx):
        await ctx.send(self.deck.stringOrderPlayers())
        
async def setup(bot):
    await bot.add_cog(DeckManager(bot))