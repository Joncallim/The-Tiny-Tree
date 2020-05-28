# The Tiny Tree (Discord DnD Bot)

## Changelog

### 27 May 2020:

- Minor bug fix to do with initiative rolls.
- Beginning to switch bot's output text over from Markdown to Embedded text.
	- Reworked dice roll text to be a little bit prettier, with embedded text and mentions included.
- Fix for the `/party` cog not flagging a non-existent item if a player tries to remove it, also added a flag for adding an item that already exists (it used to just overwrite anything with the same name).
	

- Some rewrite of the `combat_helper` cog:
	- Added a `combat_class` class to help with managing the party during combat, and re-worked some combat initialisation mechanisms to allow for easier expansion in the future.
	- Created the `/kill X` function for the DM, allowing characters to be removed from the turn order.
	- Created the `/turnorder` function, which allows anyone from the party to view the current turn order.

	
- Rewrite of `helper` cog:
	- Removed the `convert` command from `currency`, and gave it a seperate command. (i.e. `/convert 10 gp to sp` now as opposed to `/currency convert 10 gp to sp`.
	- Added a `/currency rates` command to obtain all the exchange rates.
	- Rewrote the spell helper so it's not accessing the spell JSON every time, and pre-loading the spell data to memory on first initialise.
	- Reworked the output text so it's all embedded text now.
	- Reworked the cog so that currency and spells are a seperate function each, making for slightly simpler coding for future versions.


---

### 15 May 2020:

- First release ready for use. Stable release hosted on Google Cloud compute, bot deployed to Dungeons and Diseases. Cogs are:
	1. Combat Helper
	2. Dice
	3. Helper
	4. Party 
	5. Player 
	
- Todo:
	- Introduce money transfer function.
	- Google Docs integration for party inventory (current handling is exclusively in .json locally)
	- Ambient noise generator with a nice big library of looping sounds (rainforest, cave, etc.)
	- Picture commands for DM to introduce images quickly if needed.
	- Individual inventory management.

---
