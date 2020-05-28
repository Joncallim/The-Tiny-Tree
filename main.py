#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 20:25:29 2020

@author: Jonathan
"""

import sys
# Needed to make sure the going up a level in the file manager works.
sys.path.append('../')
import discord
import random
import json
from functions import combat_class


from discord.ext import commands
import os

import nest_asyncio
nest_asyncio.apply()


with open('../tt_secret/bot_codes.json', 'r') as file:
    codes = json.load(file)

TOKEN = codes.get('token-test')
GUILD = codes.get('server')

bot = commands.Bot(command_prefix = '/')

bot.combat_class = combat_class()
bot.roll_verbose = True

bot.tree_lord_titles = ['Our Lord and Saviour the Tiny Tree',
                        'The Great Tree',
                        'The Mighty Leafy One',
                        'His Benevolence the Tiny Tree',
                        'His Great Leafiness',
                        'The Great Tree Lord',
                        'His Leafiness']
bot.entry_quotes = ['is here!',
                  'shelters us from all storms!',
                  'makes his presence known!',
                  'has arrived. All hail!',
                  'anchors us with his great roots']

# Combat states include Preparation Phase, Outside Combat, and In Combat
bot.combat_state = "Outside Combat"
bot.initiative_list = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for guild in bot.guilds:
         if guild.name == GUILD:
             break
    members = '\n - '.join([member.display_name for member in guild.members])
    print(f'Guild Members:\n - {members}')
    channel = discord.utils.get(guild.channels, name='general')
    await channel.send("```{} {}```".format(random.choice(bot.tree_lord_titles), random.choice(bot.entry_quotes)))

@bot.command(help = "Loads extensions.")
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    print('{} has now been loaded.'.format(extension))
    
@bot.command(help = "Unloads extensions.")
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    print('{} has now been unloaded.'.format(extension))
    
@bot.command(help = "Unloads extensions.")
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    print('{} has now been reloaded.'.format(extension))

    
@bot.command(name='status', help='Checks if bot is active')
async def check_status(ctx):
    await ctx.send("```{} {}```".format(random.choice(bot.tree_lord_titles), random.choice(bot.entry_quotes)))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('```You do not have the correct role for this command.```')

# This just goes through all the .py files in the cogs directory and loads them
# at the first start of this bot.
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        # Splice to cut off last 3 characters -> .py removed
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)

# Send data to DM
# user = bot.get_user(ctx.author.id)
# bot.dm_id = user
# await user.send('Initiative Starts!')