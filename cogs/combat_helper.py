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
            self.time_to_get_creatures = False
            print('Creature list has been loaded!')
            pass
        else:
            pass
        
    def set_all_initiative(self):
        # Goes through the creatures in the creature list that should have been
        # generated in the background, and appends them to the list of players.
        # This should be fairly quick, unlike accessing data from google sheets.
        for creature in self.creature_list:
            self.bot.turn_order_ids.append(creature['creature_name'])
            # Rolls initiative for each creature much like how it would be done
            # for a player. If advantage/disadvantage is specified on the sheet,
            # this data will also be retrieved, and an appropriate roll will be
            # done for them.
            if creature['init_type'] == 'normal':
                creature_initiative = random.randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
            elif creature['init_type'] == 'advantage':
                roll_1 = random.randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                roll_2 = random.randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                creature_initiative = max(roll_1, roll_2)
            elif creature['init_type'] == 'disadvantage':
                roll_1 = random.randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                roll_2 = random.randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                creature_initiative =  min(roll_1, roll_2)
            self.bot.turn_order_values.append(creature_initiative)
        # Uses ZIP to sort players and creatures by initiative, then spits out 
        # the turn order using this sort. Sorts in decreasing order, since the
        # highest initiative should go first.
        sorted_turn_order = sorted(zip(self.bot.turn_order_values, self.bot.turn_order_ids), reverse=True)
        # Ignores the secret initiative scores, just prints a list of players in
        # order of their turns.
        sorted_turn_list = [element for _, element in sorted_turn_order]
        # Just an empty array for turn_string_list
        turn_string_list = [None for x in range(len(sorted_turn_list))]
        # For each entry in the turn order, generates a string with the correct
        # number appended to the front of it.
        for i, entry in enumerate(sorted_turn_list):
            turn_string_list[i] = "{}. {}".format(str(i+1), entry)
        turnOrderString = '\n'.join(turn_string_list)
        return turnOrderString
        
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
        self.bot.turn_order_ids = []
        self.bot.turn_order_values = []
        return "```Combat is now over. Well done.```"
    
    def prepare(self):
        if self.bot.combat_state == "Preparation Phase":
            return "```Already in Preparation Phase!```"
        else:
            self.bot.combat_state = "Preparation Phase"
            # This is set to True so that only one google docs pull happens when
            # initiative is started. The creature list should then be retrieved
            # within 10 seconds of this starting - the loop is set to keep checking
            # but will not run if it is False.
            self.time_to_get_creatures = True
            self.generate_initiative()
            return "```Roll for initiative! Encounter is about to begin!```"
        
    def start(self):
        if self.bot.combat_state == "In Combat": 
            return '```Party is already in combat!```'
        elif self.bot.combat_state == "Preparation Phase":
            self.bot.combat_state = "In Combat"
            return "```Combat Begins! Turn Order:\n{}```".format(self.set_all_initiative())
        elif self.bot.combat_state == "Outside Combat":
            return self.prepare()
        
        
    @commands.command(name='combat', help='Combat Turns (DM-Only).\n1. [state] tells you the current combat phase. There are three phases: "In Combat", "Outside Combat" and "Preparation Phase". Initiative rolls can only be made during the preparation phase, and no other time.\n2. [start] turns "Outside Combat" to "Preparation Phase" and "Preparation Phase" to "In Combat".\n3. [prepare] also switches the state from "Outside Combat" to "Preparation Phase".\n4. [end] terminates combat. "In Combat" switches to "Outside Combat".\nNot entering any data brings up the current state.')
    @commands.has_role('DM')
    async def create_channel(self, ctx, arg):
        
        if arg.lower() == "state":
            combatString = '```Current combat state: {}```'.format(self.bot.combat_state)
            
        elif arg.lower() == "start":
            combatString  = self.start()
       
        elif (arg.lower() == "prepare") | (arg.lower() == "prep"):
            combatString = self.prepare()
       
        elif arg.lower() == "end":
            combatString = self.end_combat()
        
        else:
            combatString = '```This begins combat. A few things you can do here:\n1. [state] tells you the current combat phase. There are three phases: "In Combat", "Outside Combat" and "Preparation Phase". Initiative rolls can only be made during the preparation phase, and no other time.\n2. [start] turns "Outside Combat" to "Preparation Phase" and "Preparation Phase" to "In Combat".\n3. [prepare] also switches the state from "Outside Combat" to "Preparation Phase".\n4. [end] terminates combat. "In Combat" switches to "Outside Combat".\nNot entering any data brings up the current state.```'
        
        await ctx.send(combatString)
    
def setup(bot):
    bot.add_cog(combat_helper(bot))