#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 18:37:45 2020

@author: Jonathan
"""

import discord
from discord.ext import commands
import string
import json

class finance():
    
    def __init__(self, *args, **kwargs):
        with open('files/currency_info.json', 'r') as file:
            self.currency_info = json.load(file)
        self.copper = ['copper', 1]
        self.silver = ['silver', 10]
        self.electrum = ['electrum', 50]
        self.gold = ['gold', 100]
        self.platinum = ['platinum', 1000]
        
    def CurrencyInfo(self):
        embed = discord.Embed(title="Currencies in Dungeons & Dragons",
                              description=self.currency_info['info'],
                              color=0xF9E79F)
        return embed
    
    def ConvertCurrency(self, CurrencyInInput, CurrencyOutInput, OldValue):
        # First, gets the input currency Tuples from the input values.
        CurrencyIn = self.DefineCurrency(CurrencyInInput)
        CurrencyOut = self.DefineCurrency(CurrencyOutInput)
        # Checks if the Tuples are valid -- if an invalid currency was specified
        # this will be caught here.
        if (CurrencyIn is False) or (CurrencyOut is False):
            embed = discord.Embed(title="Invalid Currency",
                                  description="Valid currencies are: copper, silver, electrum, gold, and platinum.",
                                  color=0xF9E79F)
            return embed
        # Calculating the value of the output currency
        NewValue = OldValue * (CurrencyIn[1] / CurrencyOut[1])
        # Test for < 1 -- You can't have partial currencies, so tells you off 
        # if you try to make such a conversion.
        if NewValue < 1:
            embed = discord.Embed(title="Invalid Amount",
                                  description="You need to more {} to convert to {}".format(CurrencyIn[0], CurrencyOut[0]),
                                  color=0xF9E79F)
            return embed
        else:
            # The actual embedded message for conversion.
            embed = discord.Embed(title="{:,} {} gets you {:,} {}.".format(OldValue, CurrencyIn[0], NewValue, CurrencyOut[0]),
                              description="1 {} is worth {:,} {}".format(CurrencyOut[0], (CurrencyOut[1]/CurrencyIn[1]), CurrencyIn[0]),
                              color=0xF9E79F)
            return embed
    
    def DefineCurrency(self, InputCurrency):
        # Perfoms the string check for the various currencies involved here.
        if (InputCurrency.lower() == "cp") | (InputCurrency.lower() == "copper"):
            return self.copper
        elif (InputCurrency.lower() == "sp") | (InputCurrency.lower() == "silver"):
            return self.silver
        elif (InputCurrency.lower() == "ep") | (InputCurrency.lower() == "electrum"):
            return self.electrum
        elif (InputCurrency.lower() == "gp") | (InputCurrency.lower() == "gold"):
            return self.gold
        elif (InputCurrency.lower() == "pp") | (InputCurrency.lower() == "platinum"):
            return self.platinum
        else:
            return False
        
    def GetRates(self):
        # Simply prints out all the currency values relative to copper's 1-piece
        # value.
        ConversionRates = "{}: {}\n{}: {}\n{}: {}\n{}: {}\n{}: {}".format(self.copper[0], self.copper[1], self.silver[0], self.silver[1], self.electrum[0], self.electrum[1], self.gold[0], self.gold[1], self.platinum[0], self.platinum[1])
        embed = discord.Embed(title="Conversion Rates",
                              description=ConversionRates,
                              color=0xF9E79F)
        return embed

# The "spells" class preloads all the spell information, and then allows each
# spell to be called as an embed.
class spells():
    def __init__(self, *args, **kwargs):
        # Loads the spell list into the spells class to start off with. Class-
        # based work now allows for faster expansion of the project in future
        # iterations.
        with open('files/spell_data_long.json', 'r') as file:
            self.SpellList = json.load(file)
            
    def GetSpell(self, SpellName):
        Spell = self.SpellList.get(SpellName)
        # The spell description will always show up, so this initial section
        # is always active.
        embed = discord.Embed(title=SpellName,
                              description="{}, {}\nCasting Time: {}\nRange: {}\nComponents: {}\nDuration: {}".format(Spell.get('school'), Spell.get('level'), Spell.get('casting_time'), Spell.get('range'), Spell.get('components'), Spell.get('duration')),
                              color=0xA569BD)
        embed.add_field(name = "Description:",
                        value = Spell.get('desc'),
                        inline = False)
        if Spell.get('higher_level') == None:
            return embed
        else:
            # if there is a higher-level component to the spell, then this little
            # bit is added on to the end.
            embed.add_field(name = "Higher Level:",
                            value = Spell.get('higher_level'),
                            inline = False)
            return embed
            

class helper(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.finance = finance()
        self.spells = spells()
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('The helper Cog is now online.')
    
    @commands.command(name='spell', help="Spell Helper.\nEnter the name of the spell you want to look up after /spell (e.g. /spell guiding bolt). This is case insensitive, and includes spells from lots of different sources, so if your spell doesn't show up, check spelling and any apostrophes needed again.")
    async def spell_helper(self, ctx, *arg):
        # Changes text to intial caps. Note that this is going to be absolutely 
        # ruined by any lack of spaces, but at least capitalisation won't be an 
        # issue.
        spell_name = string.capwords(' '.join(arg[:]))
        await ctx.send(embed = self.spells.GetSpell(spell_name))
    
    @commands.command(name='currency', help="Brings up a nice little bit of blurb about money, just a bit of text to read if you're really bored. [/currency rates] gets you the conversion rate table.")
    async def currency(self, ctx, *args):
        if args[0] == 'rates':
            await ctx.send(embed = self.finance.GetRates())
        else:
            await ctx.send(embed = self.finance.CurrencyInfo())
    
    @commands.command(name='convert', help="Converts one currency to another. The syntax for this should be [/convert 10 gp to sp] or [/convert 100 copper to silver].")
    async def convert(self, ctx, *args):
        if args[2].lower() == 'to':
            await ctx.send(embed = self.finance.ConvertCurrency(args[1], args[3], int(args[0])))
        else:
            embed = discord.Embed(title="Invalid Syntax.",
                                      description="Specify an input currency and output currency using `/convert 10 gp to sp`, with the desired input quantity and currency, and desired output currency.",
                                      color=0xF9E79F)
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(helper(bot))
    


