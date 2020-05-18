#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 19:27:21 2020

@author: Jonathan
"""

import sys
# Needed to make sure the going up a level in the file manager works.
sys.path.append('../')
import discord
from discord.ext import commands
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials

class transfer(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        # use creds to create a client to interact with the Google Drive API
        # Opens early to try speed things up.
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('../tt_secret/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.player_sheet = client.open("Character Details").sheet1
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('The transfer Cog is now online.')

def setup(bot):
    bot.add_cog(transfer(bot))