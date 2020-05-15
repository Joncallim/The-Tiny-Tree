#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 19:27:21 2020

@author: Jonathan
"""


import discord
from discord.ext import commands
import random
import re

class transfer(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        # use creds to create a client to interact with the Google Drive API
        # Opens early to try speed things up.
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('files/client_secret.json', scope)
        client = gspread.authorize(creds)
        self.player_sheet = client.open("Character Details").sheet1
    
    def add_to_player(self):
        