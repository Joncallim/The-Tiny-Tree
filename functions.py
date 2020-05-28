#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 27 21:39:42 2020

@author: Jonathan
"""

from random import randint

class combat_class():
    
    def __init__(self, *args, **kwargs):
        self.RolledInitiative = []
        self.PlayerNames = []
        
    def reset(self):
        self.RolledInitiative = []
        self.PlayerNames = []
        
    def AddPlayerToTurnOrder(self, player, initiative):
        self.RolledInitiative.append(initiative)
        self.PlayerNames.append(player)
        
    def AddCreaturesToTurnOrder(self, creature_list):
        # Goes through the creatures in the creature list that should have been
        # generated in the background, and appends them to the list of players.
        # This should be fairly quick, unlike accessing data from google sheets.
        for creature in creature_list:
            self.PlayerNames.append(creature["creature_name"])
            # Rolls initiative for each creature much like how it would be done
            # for a player. If advantage/disadvantage is specified on the sheet,
            # this data will also be retrieved, and an appropriate roll will be
            # done for them.
            if creature['init_type'] == 'normal':
                creature_initiative = randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
            elif creature['init_type'] == 'advantage':
                roll_1 = randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                roll_2 = randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                creature_initiative = max(roll_1, roll_2)
            elif creature['init_type'] == 'disadvantage':
                roll_1 = randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                roll_2 = randint(1,20) + creature['initiative'] + (0.01 * creature['dexterity'])
                creature_initiative =  min(roll_1, roll_2)
            self.RolledInitiative.append(creature_initiative)
            pass
        
    def GetSortedString(self):
        # Just an empty array for turn_string_list
        TurnString = [None for x in range(len(self.PlayerNames))]
        # For each entry in the turn order, generates a string with the correct
        # number appended to the front of it.
        for i, entry in enumerate(self.PlayerNames):
            TurnString[i] = "{}. {}".format(str(i+1), entry)
        OutputTurnString = '\n'.join(TurnString)
        return OutputTurnString
    
    def GetSortedTurns(self):
        # Uses ZIP to sort players and creatures by initiative, then spits out 
        # the turn order using this sort. Sorts in decreasing order, since the
        # highest initiative should go first.
        SortedTurnOrder = sorted(zip(self.RolledInitiative, self.PlayerNames), reverse=True)
        # Ignores the secret initiative scores, just prints a list of players in
        # order of their turns.
        self.PlayerNames = [element for _, element in SortedTurnOrder]
        return self.GetSortedString()
    
    def RemovePlayer(self, PlayerIndex):
        self.PlayerNames.pop(PlayerIndex - 1)
        return self.GetSortedString()
    
    
    
# combat_class = combat_class()

# combat_class.AddPlayerToTurnOrder('Jon', 20)
# combat_class.AddPlayerToTurnOrder('Person', 15)
# combat_class.AddPlayerToTurnOrder('Fink', 14)

# creatures = [{"creature_name": "Dire Wolf", "init_type": "normal", "initiative": 0, "dexterity": 11},
#               {"creature_name": "Dire Wolf 2", "init_type": "normal", "initiative": 2, "dexterity": 14},
#               {"creature_name": "Dire Wolf 3", "init_type": "normal", "initiative": 1, "dexterity": 12}]

# combat_class.AddCreaturesToTurnOrder(creatures)

# print(combat_class.GetSortedTurns())

# print(combat_class.RemovePlayer(3))
