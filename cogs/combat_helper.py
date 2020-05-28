#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:44:26 2020

@author: Jonathan
"""

import sys
# Needed to make sure the going up a level in the file manager works.
sys.path.append('../')
import discord
from discord.ext import commands, tasks

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import random

class combat_helper(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.creature_list = {}
        self.time_to_get_creatures = False
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('../tt_secret/client_secret.json', scope)
        self.client = gspread.authorize(creds)
        
        self.get_creatures.start()
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('The combat Cog is now online.')
    
    # Runs the retrieve_creatures command in the background so you can initiate
    # combat quickly once everyone has rolled initiative.
    @tasks.loop(seconds = 10.0)
    async def get_creatures(self):
        if self.time_to_get_creatures:
            # Gets the workbook called "encounter creatures" and copies out all the
            # data as the creature list.
            sheet = self.client.open("Encounter Creatures").sheet1
            self.creature_list = sheet.get_all_records()
            self.bot.combat_class.AddCreaturesToTurnOrder(self.creature_list)
            self.time_to_get_creatures = False
            print('Creature list has been loaded!')
            pass
        else:
            pass
        
    def generate_initiative(self):
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = self.client.open("Character Details").sheet1
        # Calls the entire workbook to iterate through
        player_list = sheet.get_all_records()
        # Cleans the initiative list every time the preparation phase is entered.
        # This just resets all the initiatives, in case they were changed in the
        # last who-knows-how-long
        self.bot.initiative_list = {}
        for player in player_list:
            self.bot.initiative_list[str(player['player_ID'])] = {}
            self.bot.initiative_list[str(player['player_ID'])]['init'] = player['initiative']
            self.bot.initiative_list[str(player['player_ID'])]['dex'] = player['dexterity']
        pass
    
    # These functions are pretty much what they say on the tin - nothing special,
    # and the strings make it fairly obvious what's happening. Jump around as 
    # needed. 
    def end_combat(self):
        # Sets the combat state to outside combat, then scrubs the turn order
        # lists so they're empty for the next time we encounter combat.
        self.bot.combat_state = "Outside Combat"
        self.bot.combat_class.reset()
        combatEmbed = discord.Embed(title="Combat is now over!",
                                    description="Well done on surviving the encounter.",
                                    color=0xFF0000)
        return combatEmbed
    
    def prepare(self):
        if self.bot.combat_state == "Preparation Phase":
            combatEmbed = discord.Embed(title="Already in Preparation Phase!",
                                        description="Use `/combat start` to begin combat",
                                        color=0xFF0000)
            return combatEmbed
        else:
            self.bot.combat_state = "Preparation Phase"
            # This is set to True so that only one google docs pull happens when
            # initiative is started. The creature list should then be retrieved
            # within 10 seconds of this starting - the loop is set to keep checking
            # but will not run if it is False.
            self.time_to_get_creatures = True
            self.generate_initiative()
            combatEmbed = discord.Embed(title="Roll for initiative!",
                                        description="Encounter is about to begin! You can use `/r init`, `/r init a` if you have advantage, or `/r init d` if you have disadvantage.",
                                        color=0xFF0000)
            return combatEmbed
        
    def start(self):
        if self.bot.combat_state == "In Combat": 
            combatEmbed = discord.Embed(title="The party is already in combat!",
                                        description="Use `/combat end` to terminate combat",
                                        color=0xFF0000)
            return combatEmbed
        elif self.bot.combat_state == "Preparation Phase":
            self.bot.combat_state = "In Combat"
            combatEmbed = discord.Embed(title="Combat Begins!",
                                        color=0xFF0000)
            combatEmbed.add_field(name = "Turn Order:",
                                  value = "{}".format(self.bot.combat_class.GetSortedTurns()),
                                  inline = True)
            return combatEmbed
        elif self.bot.combat_state == "Outside Combat":
            return self.prepare()
        
        
    @commands.command(name='combat', help='Combat Turns (DM-Only).\n1. [state] tells you the current combat phase. There are three phases: "In Combat", "Outside Combat" and "Preparation Phase". Initiative rolls can only be made during the preparation phase, and no other time.\n2. [start] turns "Outside Combat" to "Preparation Phase" and "Preparation Phase" to "In Combat".\n3. [prepare] also switches the state from "Outside Combat" to "Preparation Phase".\n4. [end] terminates combat. "In Combat" switches to "Outside Combat".\nNot entering any data brings up the current state.')
    @commands.has_role('DM')
    async def combat(self, ctx, arg):
        
        if arg.lower() == "state":
            combatEmbed = discord.Embed(title="Current combat state:",
                                        description="{}".format(self.bot.combat_state),
                                        color=0xFF0000)
            
        elif arg.lower() == "start":
            combatEmbed  = self.start()
       
        elif (arg.lower() == "prepare") | (arg.lower() == "prep"):
            combatEmbed = self.prepare()
       
        elif arg.lower() == "end":
            combatEmbed = self.end_combat()
        
        else:
            combatEmbed = discord.Embed(title="Combat:",
                                        description="Help and information",
                                        color=0xFF0000)
            combatEmbed.add_field(name = "`/combat state`:",
                                  value = "This tells you the current combat phase. There are three phases: *'In Combat'*, *'Outside Combat'* and *'Preparation Phase'*. Initiative rolls can only be made during the preparation phase, and no other time.",
                                  inline = False)
            combatEmbed.add_field(name = "`/combat start`:",
                                  value = "This changes the combat state from *'Outside Combat'* to *'Preparation Phase'* and from *'Preparation Phase'* to *'In Combat'*.",
                                  inline = False)
            combatEmbed.add_field(name = "`/combat prepare`:",
                                  value = "This changes the combat state from *'Outside Combat'* to *'Preparation Phase'*.",
                                  inline = False)
            combatEmbed.add_field(name = "`/combat end`:",
                                  value = "This will terminate combat. The combat state will change from *'In Combat'* to *'Outside Combat'*",
                                  inline = False)
            combatEmbed.add_field(name = "`/kill X`:",
                                  value = "Can be used to remove any player or NPC from the turn order. **X** corresponds to the player's number in the turn order. Note this **cannot** be undone.",
                                  inline = False)
            combatEmbed.add_field(name = "`/turnorder`:",
                                  value = "Allows **any** player to view the current active turn order.",
                                  inline = False)
        
        await ctx.send(embed = combatEmbed)
        
    @commands.command(name='kill', help='(DM-Only) Kills a player in the turn order, typically a creature. Note that this action **cannot** be undone. Uses the index number to kill. i.e. [/kill 1] will kill the first player in the turn order.')
    @commands.has_role('DM')
    async def kill(self, ctx, arg):
        if (self.bot.combat_state == "In Combat") & (len(self.bot.combat_class.PlayerNames) > 1) & (int(arg) < (len(self.bot.combat_class.PlayerNames) + 1)):
            newTurnString = self.bot.combat_class.RemovePlayer(int(arg))
            embed = discord.Embed(title="Character killed!",
                                  color=0xFF0000)
            embed.add_field(name = "New Turn Order:", 
                            value = newTurnString, 
                            inline = True)
            
        else:
            embed = discord.Embed(title="You can't do that right now!",
                                  description="You need to:\n - Be *in combat*.\n - Have more than 1 character remaining in the turn order.\n - Select a player curently in the turn order.",
                                  color=0xFF0000)
        await ctx.send(embed = embed)
    
    @commands.command(name='turnorder', help="Displays the current turn order. If in combat, shows the active turn order. Otherwise, doesn't.")
    async def turnorder(self, ctx):
        if self.bot.combat_state == "In Combat":
            embed = discord.Embed(title="In Combat!",
                                  color=0xFF0000)
            embed.add_field(name = "Turn Order:", 
                            value = "{}".format(self.bot.combat_class.GetSortedString()), 
                            inline = True)
        else:
            embed = discord.Embed(title="You can't do that right now!",
                                  description="The party needs to be in combat for an active turn order to be generated.",
                                  color=0xFF0000)
        await ctx.send(embed=embed)
    
def setup(bot):
    bot.add_cog(combat_helper(bot))