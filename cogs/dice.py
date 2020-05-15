#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 17:57:31 2020

@author: Jonathan
    This is the Cog for dice rolling. It has a few features that make it a bit more 
powerful than a simple RNG. I've used 'r' as the command because /r is a lot faster
to type than '/roll.'
    Can be integrated into any discord bot, or just used with my main function
as-is. Takes inputs exactly as specified in the function.
"""
import discord
from discord.ext import commands
import random
import re

class dice(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
        # nat_toggle switches for 1 = Nat 20, 2 = Nat 1, and 0 = normal rolls.
        self.nat_toggle = 0 
        # dice_total is the total score for a particular roll.
        self.dice_indiv = []
        self.dice_total = 0
        # Each dice is rolled and stored in the individual_outputs list, which
        # is used to total up the scores, and also for printing later.
        self.dice_max = 0
        # For advantage/disadvantage rolls, used to store the second value
        self.dice_indiv_2 = []
        self.dice_total_2 = 0
        self.advantage = False
        self.disadvantage = False
        self.verbose = True
        self.initiative = False
    
    # Quick clean-up in case I missed any values later on in the code. Probably
    # not strictly necessary, but it helps with bolting-on parts if anything isn't
    # reassigned properly
    def reset_all(self):
        self.nat_toggle = 0 
        # dice_total is the total score for a particular roll.
        self.dice_indiv = []
        self.dice_total = 0
        self.dice_indiv_2 = []
        self.dice_total_2 = 0
        self.dice_max = 0
        # For advantage/disadvantage rolls, used to store the second value
        self.advantage = False
        self.disadvantage = False
        self.initiative = False
        pass
        
    def get_totals(self):
        self.dice_total = sum(self.dice_indiv)
        self.dice_total_2 = sum(self.dice_indiv_2)
        pass
    
    def percentage_max(self): 
        return self.dice_total / self.dice_max
    
    # Iterates through the string and if a + or - shows up handles it appropriately
    # by appending a True or False to a binary list.
    def get_plus_minus(self, dice_inputs):
        # Handling for the very first value, in case a - shows up. Otherwise,
        # assumes it will be positive and continues.
        if dice_inputs[0]  == '-':
            add_or_subtract = [False]
        else:
            add_or_subtract = [True]
        # This is only iterated from the 2nd entry in case the first character 
        # is a '-'. Doesn't really matter if it's a 1 or a 1d20, this first
        # character can almost always be ignored.
        for i in dice_inputs[1:]:
            if i == '+':
                # This simply appends a bool to the end of each list. If the 
                # value found is a +, appends True, and similiarly False 
                # for a -.
                add_or_subtract.append(True)
            elif i == '-':
                add_or_subtract.append(False)
        return add_or_subtract
    
    # This function updates the dice rolls whenever a roll is called. Does what
    # it says on the tin - rolls dice.
    def dice_roll(self, dice_inputs):
        add_or_subtract = self.get_plus_minus(dice_inputs)
        # Splits all the dice using a + or - as an indicator. There should be 
        # no whitespaces left, so the program shouldn't have an issue handling any
        # data from this point on, unless a non-integer or non-d/D is found.
        split_dice = re.split('\+|\-',dice_inputs)
        # If the first character is '-', this catches that case and deletes the
        # first entry. It's a problem with re.split, but hardly takes any time
        # so I can't really be bothered to optimise it away.
        if split_dice[0] == '':
            split_dice = split_dice[1:]
        # Crit/fail toggle here works well to pass information around
        for i, entry in enumerate(split_dice):
            # Split each nDm into n and m components. If no split is found, 
            # then it the function goes straight into handling the number as an
            # integer instead of getting the random value.
            individual_dice = re.split('d|D',entry)
            # Check for a + or -. A True is a + and a False is a -. Goes to the 
            # appropriate bit of code for it.
            if add_or_subtract[i]:
                # If a dice has two  components, i.e. n and m for an nDm dice, 
                # the program will roll an m-sided die n number of times.
                if (len(individual_dice)) == 2:
                    # Just counting up for n m-sided dice. Note that inputs are
                    # always strings, so conversion to integers is quite important
                    # for calculations to work.
                    for dice_count in range(int(individual_dice[0])):
                        # Individual roll. random.randint() is used as it gets
                        # and integer from x to y, inclusive. Essentially gets a
                        # random number from 1 to m. This value is appended to 
                        # individual_outputs for a summation later.
                        rolled = random.randint(1, int(individual_dice[1]))
                        self.dice_indiv.append(rolled)
                        # inidividual_outputs.append(rolled)
                        # Adds on the maximum possible value for any dice to 
                        # be rolled. Gives some nice stats, and is really not
                        # computationally heavy.
                        self.dice_max = self.dice_max + int(individual_dice[1])
                        # This first checks if the first dice rolled was a
                        # 1d20. (Since only a 1d20 + extras roll is counted as a
                        # crit or failure. nat_toggle switches to 1 if a crit is
                        # rolled,
                        if (individual_dice[0] == "1") & (individual_dice[1] == "20") & (rolled == 20):
                            self.nat_toggle = 1
                        # If ALL dice rolled are natural 1s, sets nat_toggle 
                        # to 2. This counts as a failure, and will be treated as
                        # such.
                        if rolled == 1: 
                            self.nat_toggle = 2
                        else:
                            self.nat_toggle = 0
                        # If there is advantage/disadvantage, makes a second
                        # set of rolls to store and save.
                        if self.advantage | self.disadvantage:
                            rolled = random.randint(1, int(individual_dice[1]))
                            self.dice_indiv_2.append(rolled)
                            # Sets the crit and fail toggles exactly the same
                            # way as with normal rolls.
                            if (individual_dice[0] == "1") & (individual_dice[1] == "20") & (rolled == 20):
                                self.nat_toggle = 1
                            if rolled == 1: 
                                self.nat_toggle = 2
                            else:
                                self.nat_toggle = 0
                else:
                    # If the value is positive, but doesn't need to be rolled,
                    # it's just appended to the list, and added on to the max
                    # possible value as well.
                    self.dice_indiv.append(int(individual_dice[0]))
                    self.dice_max = self.dice_max + int(individual_dice[0])
                    # Repeated if a second roll needs to be used.
                    if self.advantage | self.disadvantage:
                        self.dice_indiv_2.append(int(individual_dice[0]))
            # This section handles the -ve dice rolls or modifiers. It, of 
            # course, assumes that values in add_or_subtract are all bools, so 
            # anything that isn't True... is False.
            else:
                if (len(individual_dice)) == 2:
                    for dice_count in range(int(individual_dice[0])):
                        # Just makes the roll -ve, and appends it as normal, so
                        # the arithmetic to get the totals is fairly simple.
                        rolled = - random.randint(1, int(individual_dice[1]))
                        self.dice_indiv.append(rolled)
                        # The minimum roll for a -ve roll is always 1, so the 
                        # max taken off is still just 1.
                        self.dice_max = self.dice_max - 1
                        # Advantage/Disadvantage second roll. Remember that the
                        # random integer needs to be generated again...
                        if self.advantage | self.disadvantage:
                            rolled = - random.randint(1, int(individual_dice[1]))
                            self.dice_indiv_2.append(rolled)
                        # Negative rolls do not count to crits or 0s
                else:
                    self.dice_indiv.append(-int(individual_dice[0]))
                    self.dice_max = self.dice_max - int(individual_dice[0])
                    if self.advantage | self.disadvantage:
                        self.dice_indiv_2.append(-int(individual_dice[0]))
        self.get_totals()
        pass
    
    # Tidy little function to generate all the possible dice stats that need to
    # be printed. 
    def roll_print(self, dice_inputs, author_name):
        dice_str_out = dice_inputs.lower().strip().replace(" ", "").replace("+", " + ").replace("-", " - ")
        # passes author through so it can be used to get initiative for that one
        # little string, and the display names for everything else. First checks 
        # if it's an initiative roll...
        if self.initiative:
            str_0 = '{} rolls for initiative'.format(author_name)
        else:
            str_0 = '{} rolls the dice'.format(author_name)
        # Now, if it's an advantage or disadvantage roll. These are all fairly 
        # straightforward, it's just putting fancy words in strings.
        if self.advantage:
            str_1 = '{} with advantage'.format(str_0)
        elif self.disadvantage:
            str_1 = '{} with disadvantage'.format(str_0)
        else: 
            str_1 = str_0
        # Checking to see if a crit was had. Crits don't happen on initiative
        # rolls so this is fine to stay in the main loop. Since non-crits happen
        # most regularly, this is the first if-term... So the search doesn't 
        # need to be made every single time.
        if self.nat_toggle == 0:
            str_2 = f"{str_1}!"
        elif self.nat_toggle == 2:
            str_2 = f"{str_1} and fails miserably!"
        else:
            str_2 = f"{str_1} and gets a Crit!"
        # Initiative string!!! Initiative rolls don't care about verbosity, so
        # this set lives apart from the others. If it's an initiative roll, the
        # string is returned from these statements, skipping the rest of the 
        # function.
        if self.initiative:
            if self.advantage | self.disadvantage:
                outputString = "```{}/nInitiative: [{}]\nRoll 1: [{}], Roll 2: [{}]\n({})```".format(str_2, max(self.dice_total,self.dice_total_2),  self.dice_total, self.dice_total_2, dice_inputs)
                return outputString
            else:
                outputString = "```{}\nTotal: [{}] ({})```".format(str_2, self.dice_total, dice_inputs)
                return outputString
        if self.verbose:
            if self.advantage | self.disadvantage:
                outputString = """```{}\nTotal 1: [{}]; Total 2: [{}]\nRoll 1: {}; Roll 2: {};\nInput: [{}]; Maximum Possible: {}```""".format(str_2, self.dice_total, self.dice_total_2, self.dice_indiv, self.dice_indiv_2, dice_str_out, self.dice_max)
                return outputString
            else:
                outputString = """```{} Total: {}\nIndividual: {}; Input: [{}]\nMaximum Possible: {}; Percentage of Max Roll: {:.2f}%```""".format(str_2, self.dice_total, self.dice_indiv, dice_str_out, self.dice_max, self.percentage_max())
                return outputString
        else:
            if self.advantage | self.disadvantage:
                outputString = """```{}\nTotal 1: [{}]; Total 2: [{}]```""".format(str_2, self.dice_total, self.dice_total_2)
                return outputString
            else:
                outputString = f"""```{str_2} Total: {self.dice_total}```"""
                return outputString  
    
    # Does a nice check to see if the input matches any of the cases for "advantage."
    def check_double_roll(self, str_in):
        if (str_in.lower() == 'advantage') | (str_in.lower() == 'adv') | (str_in.lower() == 'a'):
            self.advantage = True
            return True
        elif (str_in.lower() == 'disadvantage') | (str_in.lower() == 'disadv') | (str_in.lower() == 'd'):
            self.disadvantage = True
            return True
        else:
            return False
    
    
    def roll_initiative(self, author):
        # Redeclaring initiative and dexterity, first because they're hella long
        # and I don't want to have to copy them again and again, but also so the
        # dict doesn't have to be searched every time.
        initiative = self.bot.initiative_list[str(author.id)].get('init')
        dexterity = self.bot.initiative_list[str(author.id)].get('dex')
        # Creates the string to print the "input" dice... Does what it says on 
        # the tin, it's not too complicated. If -ve initiative it's a 1d20 - 
        # initiative, if 0 it's just that, etc.
        if initiative < 0:
            dice_inputs = f"1d20 - {abs(initiative)}"
        elif initiative == 0:
            dice_inputs = "1d20"
        else:
            dice_inputs = f"1d20 + {abs(initiative)}"
        # Does a double roll if there is advantage or disadvantage, and then
        # gets it's secret initiative from the dice rolls + initiative. The
        # dexterity multiplier is 0.01 so basically only dex >99 will ever 
        # overtake anyone with a higher roll... But then your modifier should
        # be too big for you to be concerned with that.
        if self.advantage | self.disadvantage:
            self.dice_total = random.randint(1,20) + initiative
            self.dice_total_2 = random.randint(1,20) + initiative
            # For advantage, takes the higher of the two rolls. Similarly for
            # disadvantage, takes the lower of the two rolls.
            if self.advantage:
                secret_initiative = max(self.dice_total,self.dice_total_2) + (0.01 * dexterity)
            else:
                secret_initiative = min(self.dice_total,self.dice_total_2) + (0.01 * dexterity)
        # No advantage or anything... Just rolling the 1d20 and adding any other
        # necessary modifiers to it.
        else: 
            self.dice_total = random.randint(1,20) + initiative
            secret_initiative = self.dice_total + (0.01 * dexterity)
        # Appends the author and initiative to the turn order, which should not
        # need to be returned anywhere since it can just be done right here...
        self.bot.turn_order_ids.append(author.display_name)
        self.bot.turn_order_values.append(secret_initiative)    
        
        return dice_inputs
    
    def initiative_roll(self, author):
        # Quick check to see if the bot is currently in the prep phase. If not,
        # just tells you you can't roll for initiative yet.
        if self.bot.combat_state == "Preparation Phase":
            # Check for author existing in the turn order. You obviously can't
            # be in the turn order twice, so only allows you to roll once.
            if author.display_name not in self.bot.turn_order_ids:
                # Roll for initiative. Different function from the main one!
                dice_inputs = self.roll_initiative(author)
                # Gets the pretty text for writing the results out!
                outputString = self.roll_print(dice_inputs, author.display_name)
            else:
                outputString = "```{} has already rolled Initiative!```".format(author.display_name)   
        else:
            outputString = "```It's not time to roll initiative, {}!```".format(author.display_name)
        return outputString
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('The dice Cog is now online.')
        
    
# =========================================================================== #
# MAIN BLOCK - contains all the little bit that control the actual dice bits. #
# =========================================================================== #
    @commands.command(name = 'r', help = "Dice Rolling\n1. [/r 1d20] Simulates rolling dice. Input your NdM dice with other add-ons coupled with a '+'. For example, '/r 1d20 + 5' will roll a 1d20 and add 5, and '/r 1d20 + 3d4' will roll 1d20 and 3d4. This command ignores whitespace, so '/r 1d20+3' is equivalent to '/r 1d20 + 3'.\n2. [initiative] Initiative rolls work if you have your data stored with the bot. The bot will then automatically roll initiative for you if combat is in the appropriate state.\n3. [advantage/disadvantage] Adding advantage/disadvantage (adv/disadv/a/d also work) before your roll will automatically roll the dice twice, and take the higher/lower of the two rolls. It still shows stats from both rolls.\n4. If rolling initiative with advantage, enter /r initiative advantage.\n")
    async def roll(self, ctx, *arg):
        if self.check_double_roll(arg[0]):
            # Deletes the first argument item. Doesn't matter if it's an adv,
            # disadv, or whatever, just removes it.
            arg = arg[1:]
            # Some pre-preparation for the following work. Gets rid of all whitespace
            # and lowers the case. Doesn't always seem to work, so a catch for both d
            # and D is given later
            dice_inputs = ('{}'.format(''.join(arg))).lower()
            # Rolls the dice! The fun stuff happens here.
            self.dice_roll(dice_inputs)
            # Makes the string lowercase, strips it and removes and whitespace, then adds exactly a single space around all + and - symbols
            outputString = self.roll_print(dice_inputs, ctx.author.display_name)
        # Check if the first argument is the initiative or init argument. If 
        # it is, then goes into looking for the advantage/disadvantage rolls,
        # which it then works on... 
        elif (arg[0].lower() == 'init') | (arg[0].lower() == 'initiative'):
            # Sets the marker for self.initiative to True so that printing will
            # be handled properly later.
            self.initiative = True
            # This is the check for an advantage roll. If it's an advantage roll
            # the first 2 arguments need to be removed (i.e. init adv instead of 
            # just init.).
            if self.check_double_roll(arg[0]):
                arg = arg[2:]
            else:
                arg = arg[1:]
            outputString = self.initiative_roll(ctx.author)
        # Finally, if there are no special cases happening... Just rolls the dice.
        # Same process as in initiative, but no initiative set in self.
        else:
            dice_inputs = ('{}'.format(''.join(arg))).lower()
            self.dice_roll(dice_inputs)
            outputString = self.roll_print(dice_inputs, ctx.author.display_name)
        
        await ctx.send(outputString)
        # Resets all the variables that have a chance to muck up our function!
        self.reset_all()
        
    @commands.command(name = 'verbose', help = 'Verbosity determines how much information is shown with each roll.\n[verbose] will toggle how much information is shown when you roll a dice.')
    async def toggle_verbose(self, ctx):
        # If verbosity is toggled on (it is by default), it will show all the dice
        # stats and stuff - turn it off to have a quieter bot.
        if self.verbose:
            self.verbose = False
            outputString = "```{} grows quiet.\nDice rolls will now no longer show extra information.```".format(random.choice(self.bot.tree_lord_titles))
        else:
            self.verbose = True
            outputString = "```{} will show you the secrets of the world!\nDice rolls will now include all info.```".format(random.choice(self.bot.tree_lord_titles))
        await ctx.send(outputString)
    

def setup(bot):
    bot.add_cog(dice(bot))