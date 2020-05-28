#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 13:15:06 2020

@author: Jonathan
"""


import discord
from discord.ext import commands
import re

import json
import string



class party(commands.Cog):
    
    def __init__(self, bot):
        self.add_money = True
        self.bot = bot
    
    def check_inventory(self):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        # For each money item in the "money" dict, prints a single line, then
        # groups them line by line for each currency value.
        moneyString = ""
        for key,value in inventory['money'].items():
            moneyString = "{}{}: [{}]\n".format(moneyString, string.capwords(key), value)
        itemString = ""
        for key,details in inventory['items'].items():
            itemString = "{}\n\n{} (Value: [{} gp])\nDescription: {}".format(itemString, key, details['value'], details['desc'])
        inventoryEmbed = discord.Embed(title="Party Inventory",
                                        description="The party's joint assets, including all money and items:",
                                        color=0xECF0F1)
        inventoryEmbed.add_field(name = "Money:",
                                 value = moneyString,
                                 inline = False)
        inventoryEmbed.add_field(name = "Items:",
                                 value = itemString,
                                 inline = False)
        return inventoryEmbed
    
    
    def check_items(self):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        itemString = ""
        for key,details in inventory['items'].items():
            itemString = "{}\n\n{} (Value: [{} gp])\nDescription: {}".format(itemString, key, details['value'], details['desc'])
        inventoryEmbed = discord.Embed(title="Party Items",
                                        description="The party's jointly-owned items:{}".format(itemString),
                                        color=0xECF0F1)
        return inventoryEmbed
    
    def add_item(self, new_item):
        # There are two splitters possible - ; and / are both valid characters.
        # This takes the first entry as the name, the second entry as the item's
        # value in gp, and the third as the description. Joins all the items
        # with a single space now, but still splits them using the symbols.
        item_details = re.split('\;|\/',' '.join(new_item))
        # Takes the first entry as the item's name - capitalises the first letter
        # of every word, so 'horses of gondor' becomes 'Horses Of Gondor" which
        # isn't ideal but hey ho...
        item_name = string.capwords(item_details[0])
        # Accesses the json file with the party inventory - json used as choice
        # of database, since jsons are FAST.
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        if item_name in inventory['items']:
            inventoryEmbed = discord.Embed(title="Item already in inventory!",
                                           description="Use `/party items` to check what the party currently owns.",
                                           color=0xECF0F1)
            return inventoryEmbed
        else:
            # Second item should be the value. If a number hasn't been entered, 
            # someone has messed it up and it won't be registered. If no entry, the
            # value is set to 0. Also handles description similarly, but capitalises
            # the first word of every sentence here.
            if len(item_details) == 1:
                item_value  = 0
                item_description = "No Description"
            elif len(item_details) == 2:
                print('here')
                item_value = int(item_details[1].strip())
                item_description = "No Description"
            else:
                item_value = int(item_details[1])
                item_description = item_details[2].strip().capitalize()
            # creates a new dictionary with the item name specified, and then updates
            # the overall inventory dictionary to include this new item dictionary.
            newItem = {item_name : {'desc': item_description, 'value': item_value}}
            inventory['items'].update(newItem)
            # Saves the new inventory to the json file. sort_keys and indent are 
            # used to beautify the file, making for easier human-reading.
            with open('files/party_inventory.json', 'w') as f:
                 f.write(json.dumps(inventory, sort_keys=True, indent=4))
            inventoryEmbed = discord.Embed(title="Item Added!",
                                           description="{} has been added to the party inventory.".format(item_name),
                                           color=0xECF0F1)
            inventoryEmbed.add_field(name = "Value:",
                                     value = "{} gp".format(item_value),
                                     inline = False)
            inventoryEmbed.add_field(name = "Description",
                                     value = item_description,
                                     inline = False)
            return inventoryEmbed
    
    def remove_item(self, name):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        
        name = string.capwords(name)
        # Sanity check to make sure the item exists in the inventory. If it 
        # does, then pops it and tells you that it's been removed. If it doesn't 
        # exist, throws an error up.
        if name in inventory['items']:
            inventory['items'].pop(name)
            with open('files/party_inventory.json', 'w') as f:
                 f.write(json.dumps(inventory, sort_keys=True, indent=4))
            inventoryEmbed = discord.Embed(title="Item Removed!",
                                           description="{} has been removed from the party inventory.".format(name),
                                           color=0xECF0F1)
            return inventoryEmbed
        else:
            inventoryEmbed = discord.Embed(title="Item does not exist!",
                                           description="Use `/party items` to check what the party currently owns.",
                                           color=0xECF0F1)
            return inventoryEmbed
    
    def check_money(self):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        # Fairly strightforward - iterates through each currency stored inside
        # the list, and then copies it out to a nice long string for printing.
        moneyString = ""
        for key,value in inventory['money'].items():
            moneyString = "{}{}: [{}]\n".format(moneyString, string.capwords(key), value)
        inventoryEmbed = discord.Embed(title="Party Funds",
                                       description="The party's accountant holds:\n{}".format(moneyString),
                                       color=0xECF0F1)
        return inventoryEmbed
    
    def update_money(self, value, currency):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        # Get old value of currency stored 
        oldValue = inventory['money'].get(currency)
        if self.add_money:
            newValue = oldValue + value
        else:
            newValue = oldValue - value
            # Resets the add_money counter, so the next iteration will be an 
            # addition, if called again.
            self.add_money = True
        # Sanity check. The party can't have a negative amount of money, so if
        # this is the case, returns the statement telling you that you can't 
        # remove that much money!
        if newValue < 0:
            inventoryEmbed = discord.Embed(title="Insufficient Money!",
                                           description="The party does not have that much {}. Type /party money to check how much you currently have.".format(currency),
                                           color=0xECF0F1)
            return inventoryEmbed
        else:
            # Creates a new dict with the correct currency and new value to be 
            # updated, then updates the original list, and pushes it to the json
            # file to save. Again sort_keys and indent are used for beautification
            newMoney = {currency: newValue}
            inventory['money'].update(newMoney)
            with open('files/party_inventory.json', 'w') as f:
                 f.write(json.dumps(inventory, sort_keys=True, indent=4))
            # Returns string to show updated money amounts. Capwords just makes
            # sure that each word is initial-capsed so it looks pretty.
            moneyString = ""
            for key,amount in inventory['money'].items():
                moneyString = "{}{}: [{}]\n".format(moneyString, string.capwords(key), amount)
            inventoryEmbed = discord.Embed(title="Party funds have been updated!",
                                           description="{} {} has been added to the party's funds.".format(value, currency),
                                           color=0xECF0F1)
            inventoryEmbed.add_field(name = "Updated party fund:",
                                     value = moneyString,
                                     inline = False)
            return inventoryEmbed
        
    def remove_money(self):
        with open('files/party_inventory.json', 'r') as file:
            inventory = json.load(file)
        # This is easy, just automatically writes a new dictionary with 
        # everything set to 0, so don't need to iterate through every value
        # in the dictionary - we know exactly what should be in it, and no
        # other currencies.
        newMoney = {'platinum': 0, 'gold':0, 'electrum': 0, 'silver': 0, 'copper': 0}
        inventory['money'].update(newMoney)
        # Pushing new dict to json
        with open('files/party_inventory.json', 'w') as f:
             f.write(json.dumps(inventory, sort_keys=True, indent=4))
        inventoryEmbed = discord.Embed(title="The party now holds no collective funds.",
                                       description="Party funds have been cleared.",
                                       color=0xECF0F1)
        return inventoryEmbed
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('The party Cog is now online.')
    
    @commands.command(name='party', help="Party Inventory Management.\n1. [inventory] will show a list of all items jointly held.\n2. [items] will show only items, and exclude money. You can also write '/party items add new_item value_in_gp description' to add an item, and '/party items remove item_name' to remove any item.\n3. [money] displays the current held cash in various currencies. '/party money add amount currency' will add that amount to the appropriate bin, and '/party money remove amount currency' will remove it. You can also enter '/party money clear' to clean out the entire party's shared money.")
    async def party_helper(self, ctx, *arg):
        # Check for first argument == Inventory/inv
        if (arg[0].lower() == 'inventory') | (arg[0].lower() == 'inv'):
            inventoryEmbed = self.check_inventory()
        elif arg[0].lower()== 'items':
            if len(arg) == 1:
                inventoryEmbed = self.check_items()
            elif arg[1].lower() == 'add':
                # Sends all the arguments through to add_item... Anything else
                # can be handled there quite easily.
                inventoryEmbed =  self.add_item(arg[2:])
            elif arg[1].lower() == 'remove':
                # If you're removing an item from the inventory, just joining
                # all the strings together from the arg will be the item's 
                # name. This  must match the saved text, although should be
                # case-insensitive given how this function handles the text.
                inventoryEmbed =  self.remove_item(' '.join(arg[2:]))
        # This is the section to check if money is being used... Same process
        # as with the inventory.
        elif arg[0].lower() == 'money':
            if len(arg) == 1:
                inventoryEmbed = self.check_money()
            elif arg[1].lower() == 'add':
                # "add 50 gold" would be an appropriate input - the second argument
                # should be a number, so is converted to an integer as such.
                inventoryEmbed =  self.update_money(int(arg[2]), arg[3])
            elif arg[1].lower() == 'remove':
                # Literally the same as above, but add_money check is set to 
                # False so the command knows to remove money and not add to it.
                self.add_money = False
                inventoryEmbed =  self.update_money(int(arg[2]), arg[3])
            # This is the scrub-inventory command, basically clears all the cash
            # out of the inventory so you can distribute funds/use them.
            elif arg[1].lower() == 'clear':
                inventoryEmbed = self.remove_money()
        else:
            inventoryEmbed = discord.Embed(title="Invalid Syntax!",
                                        description="Use `/party money [options]`, where `[options]` must be in the order: `add/remove amount currency`.",
                                        color=0xECF0F1)        
        await ctx.send(embed = inventoryEmbed)
        
def setup(bot):
    bot.add_cog(party(bot))





