# The Tiny Tree (DnD Discord Bot)
## Readme

DnD discord helper for the Dungeons and Diseases game. This is a post-FYP project written by myself, and I'll add ocassional things to it as and when the inspiration strikes. Commands for this bot are all called with the `/` character. There are currently the following functions:

1. **_Dice_**, Called with the `/r` prefix. Rolls an `nDm` number of dice - where `n` is the number of dice and `m` is the number of sides per dice. This has several modifiers that can be added:
	- `ndm + ndm - ndm + x - y`, which follows the format of `n` `m`-sided die, and `x` and `y` are both constant modifiers to the roll. `+` and `-` should work anywhere in the statement (including right at the start), but note that any white space is ignored, so if you miss a `+` somewhere the numbers are just mushed together.
	- `advantage` | `adv` |  `a`, followed by the dice roll. All add advantage to your roll (i.e. roll the dice twice). They do not automatically take the higher of the two rolls - since sometimes a crit may mean you have an overall lower score.
	- `disadvantage` | `disadv` |  `d`, followed by the dice. Similarly, all add disadvantage to your roll (i.e. roll the dice twice). It will display both rolls for your viewing pleasure.
	- `initiative` | `init` only works if the DM has started the preparation phase for combat (i.e. the bot will tell you to roll for initiative. Realistically it would be simpler to have rolled initiative for everyone, but where's the fun in that...
	- `/verbose` is a separate command to `/r`, and toggles the amount of information that is shown by the bot. There are some cute prompts to tell you how much information is being shown.
	- Some neat tricks for `/r` include being able to let you know if a nat20 or nat1 has been rolled (only applies if the first dice rolled is a `1d20`).

2. **_Helper_**, a fairly useful cog that gives you information about DnD stuff. Commands are:
	- `/spell` which gives you information about any spell within *Elemental Evil*, *The Player's Handbook*, *Sword Coast Advanced Guide*, and *Xanathar's Guide to Everything*. It follows the format `/spell spell_name`. This is case-insensitive, but you need to have spelled and put and important punctuation in. So, `/spell aGGaNazzAR's SCORcher` will work, but `/spell animalfriendship` will not.
	- `/currency` tells you a bit about the conversion rate between currencies. `/currency info` brings up some useful blurb about money, especially for people (like myself) who can never remember what they all mean. `/currency convert N gp to sp` lets you convert `N` of any currency to another. This is case insensitive, and takes currency arguments as either `gp` or `gold`, `sp` or `silver`, etc.

3. **_Player_** gets you *your own* information - you can't just go mess with someone else's stats or money!
	- `money` brings up the money you currently own. This accesses data from a Google Sheet somewhere on the interwebs, but is pre-cached on the bot in order to speed up responses when you make any requests. If you absolutely **need** to update the money now because you made a change in Google Sheets, you can simply `/reload player` and it should re-download all of the necessary information. 
	- `money add n gold` | `money remove n gold` will add or remove any particular currency (not just gold) of a particular amount to your own inventory. This still only works with the specific "gold" or "silver" (etc.) words. This is an immediate Google Sheets request so will take a bit longer than the other commands.
	- `stats` brings up your stats as updated by the DM at some point. If there has been a level up, this will have been done by the DM, you shouldn't need to have to update it yourself - I understand that everyone has their own favourite ways to keep data, so kept away from too much automation.

4. **_Party_** retrieves the party inventory from a .json file. jsons are fast, so I like them (This inventory is only stored locally, and you can't really just mess around with it at will - I'll add Google Sheets integration at some point). 
 - `inventory` | `inv` brings up the total party inventory (money and items).
 - `money` shows all of the various currencies that the party jointly holds. You can add/remove money with `/party money add 50 gold`/`/party money remove 50 gold`.
 - `items` brings up the items that the players holds (sans money.) You can add items as well, in the format `/party items add item name; value; item description`. You can use either `[ ; ]` or `[ / ]` as a seperator, and the value should be an integer number in gp (the item name and description can be of any length). Similarly, `/party items remove item name` will remove that item from the party inventory.

5.  **_Combat Helper_**, helps to start initiative, etc. Only rollable by DM. Does a check every 10 seconds to see if it needs to pull data from Google Drive, and if it does it will load all initiative and Pulls data from Google Drive while everyone is rolling initiative. (Within 10 seconds, so don't start combat too soon after initiating it)
	- `/combat start` will start the initiative-rolling phase if the party is currently outside combat, and starts combat if the party is currently in the initiative phase. When combat is started, all encounter creatures have initative rolled for them automatically, and the DM should have already updated the google form *before* starting the preparation phase.
	- `/combat prepare` | `combat prep` moves the party in the initiative-rolling phase. When in this phase, players can use the `/r init` to roll for initiative. `/r init adv` rolls initiative with advantage automatically.
	- `/combat end` ends combat, like it says.
	- `/combat state` will tell you which phase you're currently in. Again, only the DM can do this.

6. **_No Category_** are just some general-purpose commands that help you out a little.
	- `/load Cog` loads a particular module (all the sections above are "Cogs" in `discord.py`, or classes in Python.
	- `/unload Cog` unloads...
	- `/reload Cog` unloads... then loads.
	- `/status` just gives you some nice confirmation that the bot is online by printing some text.


Google Sheets requests run in the background as much as possible using `@tasks.loop` so that commands are responded to faster (particularly initiative rolls, unfortunately money updates still need an immediate update to happen so will take a while).

-

### Links:

- [Add Release Version to Server](https://discord.com/api/oauth2/authorize?client_id=709719343822405724&permissions=2013789296&scope=bot)
- [Add Test Version to Server](https://discord.com/api/oauth2/authorize?client_id=709009411900833792&permissions=8&scope=bot)
- [Discord.py Reference](https://discordpy.readthedocs.io/en/latest/index.html#)