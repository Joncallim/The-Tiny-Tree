#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 17:36:11 2020

@author: Jonathan

Tasks are used in this Cog to cache everything from the google docs - this helps
to dramatically speed up response times, but puts a bit more drain on bandwidth.
"""

import sys
# Needed to make sure the going up a level in the file manager works.
sys.path.append('../')
import discord
from discord.ext import commands, tasks

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class player_commands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.player_info = {}
        self.currency_column = {}
        # use creds to create a client to interact with the Google Drive API
        # Opens early to try speed things up.
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('../tt_secret/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.player_sheet = client.open("Character Details").sheet1
        
        self.player_list = {}
        self.player_list = self.player_sheet.get_all_records()
        
        self.retrieve_player_info.start()
        self.get_all_money_columns.start()
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('The player Cog is now online.')
        
    # Runs the retrieve_creatures command in the background so you can initiate
    # combat quickly once everyone has rolled initiative.
    @tasks.loop(seconds = 1800.0)
    async def retrieve_player_info(self):
        self.player_list = self.player_sheet.get_all_records()
        print('Player info has been successfully updated.')
        pass
    
    # This is done every 24 hours - the assumption is that the locations of the
    # money columns should not change. If a reload is desperately needed, then
    # you could just reload the entire module.
    @tasks.loop(seconds = 86400.00)
    async def get_all_money_columns(self):
        currencies = ['platinum', 'gold', 'electrum', 'silver', 'copper']
        for currency in  currencies:
            new_column = {currency: self.player_sheet.find(currency).col}
            self.currency_column.update(new_column)
        print('Currency columns have been successfully updated.')
        pass
    
    # Searches for the appropriate row and column number, and uses these values
    # appropriately.
    def update_money(self, userID, currency, amount, increase=True):
        # converts "currency" to lowercase so it always works with the sheet.
        currency = currency.lower()
        # Get column  and row of the desired currency
        row_ident = self.player_sheet.find(str(userID)).row
        col_ident = self.currency_column.get(currency)
        # Find original amount of money, and add or subtract as needed.
        original_val = self.player_sheet.cell(row_ident, col_ident).value
        if increase:
            new_val = int(original_val) + int(amount)
        else:
            new_val = int(original_val) - int(amount)
        if new_val < 0:
            return 'fail'
        else:
            self.player_sheet.update_cell(row_ident, col_ident, new_val)
            return new_val
        
    # Returns the player as an array so that the category can be used. Need to 
    # iterate through the whole list because of shitty gdocs formatting
    def get_player(self, userID):
        for player in self.player_list:
            if player['player_ID'] == int(userID):
                self.player_info = player
    
    # Easy enough -- Uses a user's discord ID to reference the doc. That way 
    # this doesn't change even with a different display name or username (Stuff
    # that can be changed. Same as with money.)
    def get_player_details(self, userID):
        self.get_player(userID)
        charDetailsString = '''```{}\nInitiative: [{}]\nAC: [{}]\nStrength: [{}]\nDexterity: [{}]\nConstitution: [{}]\nIntelligence: [{}]\nWisdom: [{}]\nCharisma: [{}]```'''.format(self.player_info['char_name'], self.player_info['initiative'], self.player_info['armour_class'], self.player_info['strength'], self.player_info['dexterity'], self.player_info['constitution'], self.player_info['intelligence'], self.player_info['wisdom'], self.player_info['charisma'])
        return charDetailsString
    
    def get_player_money(self, userID):
        self.get_player(userID)
        moneyString = '''```{}\nPlatinum: {}, Gold: {}, Electrum: {}, Silver: {}, Copper: {}```'''.format(self.player_info['char_name'], self.player_info['platinum'], self.player_info['gold'], self.player_info['electrum'], self.player_info['silver'], self.player_info['copper'])
        return moneyString

    @commands.command(name='player', help="Player Details.\n1. [money] will display the current money you have, as stored in the Google Sheet.\n2. [stats] or [info] will display your current stats, again as stored in the Google Sheet.\n3. [money add 50 gold] will add 50 gold to your inventory. You can enter any of the platinum, gold, electrum, silver or copper currencies, and use add/remove to add or remove an amount of currency from your inventory. It will then be automatically updated.")
    async def player(self, ctx, *arg):
        if arg[0].lower() == 'money':
            if len(arg) == 1:
                playerString = self.get_player_money(str(ctx.author.id))
            elif arg[1].lower() == 'add':
                new_amount = self.update_money(ctx.author.id, arg[3], arg[2], increase=True)
                playerString = "```{} now has {} {}!```".format(ctx.author.display_name, new_amount, arg[3])
            elif arg[1].lower() == 'remove':
                new_amount = self.update_money(str(ctx.author.id), arg[3], arg[2], increase=False)
                if new_amount == 'fail':
                    playerString = "```{} does not have that much {}!```".format(ctx.author.display_name, arg[3])
                else:
                    playerString = "```{} now has {} {}!```".format(ctx.author.display_name, new_amount, arg[3])
            else:
                playerString = '```Check your message syntax: /player money [options], where [options] must be in the order: add/remove amount currency.```'
    
        elif (arg[0].lower() == 'stats') | (arg[0].lower() == 'info'):
            playerString = self.get_player_details(str(ctx.author.id))
             
        else:
            playerString = '```You need to add an argument to the /player command. For help type /help player.```'
            
        await ctx.send(playerString)
        
    @commands.command(name="update_player_info", help="Updates player details by pulling info off google docs NOW. Otherwise, performs this action every 30 minutes.")
    async def update_player_info(self, ctx):
        self.player_list = self.player_sheet.get_all_records()
        await ctx.send('```Player details have been updated!```')
        
def setup(bot):
    bot.add_cog(player_commands(bot))
