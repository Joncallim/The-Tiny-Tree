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

class helper(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.currency_info = '''```Common coins come in several different denominations based on the relative worth of the metal from which they are made. The three most common coins are the gold piece (gp), the silver piece (sp), and the copper piece (cp).

With one gold piece, a character can buy a bedroll, 50 feet of good rope, or a goat. A skilled (but not exceptional) artisan can earn one gold piece a day. The gold piece is the standard unit of measure for wealth, even if the coin itself is not commonly used. When merchants discuss deals that involve goods or services worth hundreds or thousands of gold pieces, the transactions don’t usually involve the exchange of individual coins. Rather, the gold piece is a standard measure of value, and the actual exchange is in gold bars, letters of credit, or valuable goods.

One gold piece is worth ten silver pieces, the most prevalent coin among commoners. A silver piece buys a laborer’s work for half a day, a flask of lamp oil, or a night’s rest in a poor inn.

One silver piece is worth ten copper pieces, which are common among laborers and beggars. A single copper piece buys a candle, a torch, or a piece of chalk.

In addition, unusual coins made of other precious metals sometimes appear in treasure hoards. The electrum piece (ep) and the platinum piece (pp) originate from fallen empires and lost kingdoms, and they sometimes arouse suspicion and skepticism when used in transactions. An electrum piece is worth five silver pieces, and a platinum piece is worth ten gold pieces.

A standard coin weighs about a third of an ounce, so fifty coins weigh a pound.```'''
        self.exchange_rates = {'CP': 1, 'SP': 10, 'EP': 50, 'GP': 100, 'PP': 1000, 'COPPER': 1, 'SILVER': 10, 'ELECTRUM': 50, 'GOLD': 100, 'PLATINUM': 1000}
    
    def convert(self, amount, currency_in, currency_out):
        rate = self.exchange_rates.get(currency_in.upper()) / self.exchange_rates.get(currency_out.upper())
        output_value = amount * rate
        if len(currency_in) == 2:
            currency_in = currency_in.lower()
        else:
            currency_in = currency_in.capitalize()
        if len(currency_out) == 2:
            currency_out = currency_out.lower()
        else:
            currency_out = currency_out.capitalize()
        if output_value < 1:
            return "```You don't have enough {} to make this conversion!```".format(currency_in)
        else:
            return "```{:,} {} gets you {:,} {}.```".format(amount, currency_in, int(output_value), currency_out)
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('The helper Cog is now online.')
    
    @commands.command(name='spell', help="Spell Helper.\nEnter the name of the spell you want to look up after /spell (e.g. /spell guiding bolt). This is case insensitive, and includes spells from lots of different sources, so if your spell doesn't show up, check spelling and any apostrophes needed again.")
    async def spell_helper(self, ctx, *arg):
        with open('files/spell_data_long.json', 'r') as file:
            spell_list = json.load(file)
        # Changes text to intial caps. Note that this is going to be absolutely 
        # ruined by any lack of spaces, but at least capitalisation won't be an 
        # issue.
        spell_name = string.capwords(' '.join(arg[:]))
        # Gets actual spell's dictionary from the dict containing all the spells
        spell = spell_list.get(spell_name)
        # Returns the actual output string that's to be printed in Discord.
        if spell.get('higher_level') == None:
            outputString = '''```{}:\n{}, {}\nCasting Time: {}\nRange: {}\nComponents: {}\nDuration: {}\n\n{}```'''.format(spell_name, spell.get('school'), spell.get('level'), spell.get('casting_time'), spell.get('range'), spell.get('components'), spell.get('duration'), spell.get('desc'))
            await ctx.send(outputString)
        else:
            outputString = '''```{}:\n{}, {}\nCasting Time: {}\nRange: {}\nComponents: {}\nDuration: {}\n\n{}\n\nAt higher levels:\n{}```'''.format(spell_name, spell.get('school'), spell.get('level'), spell.get('casting_time'), spell.get('range'), spell.get('components'), spell.get('duration'), spell.get('desc'), spell.get('higher_level'))
            await ctx.send(outputString)
    
    @commands.command(name='currency', help="The currency helper helps you out a little with converting money.\n1. [info] brings up a nice little bit of blurb about money, just a bit of text to read if you're really bored.\n2. [convert n input_money to output_money] gives you the conversion rate. For example, '/currency convert 10 gold to silver' would tell you how much silver you'd get for 10 gold.")
    async def currency(self, ctx, *arg):
        if arg[0].lower() == 'info':
            await ctx.send(self.currency_info)
        if arg[0].lower() == 'convert':
            if arg[3].lower() == 'to':
                output_string = self.convert(int(arg[1]), arg[2], arg[4])
            await ctx.send(output_string)
            

def setup(bot):
    bot.add_cog(helper(bot))
    


