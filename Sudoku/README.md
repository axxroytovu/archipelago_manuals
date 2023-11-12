# ap_manual_sudoku
A manual archipelago world for playing variant sudoku

The puzzles referenced are part of the Cracking the Cryptic community's daily "Generally Accessible Sudoku" or GAS series.

More info about the CTC community can be found on their webpage, https://www.youtube.com/c/CrackingTheCryptic


# Running this game
So you want to play some sudoku? 

All you need for this is:
- An internet connection and web browser
- A download of the .apworld and .yaml file in the top level of this repository
- The Archipelago Manual client found in the Announcements channel of the Maunal AP discord server.

## Getting set up
Run the `generate.py` file to randomize your build. You can put in the total hours you hope to play for, and it will generate a randomized .apworld and .yaml file for you.

Common breakpoints:
- Sync Short: 2 hours (Sudoku really doesn't work below 2 hours)
- Sync Long: 5 hours
- Async Short: 7 hours
- Async Long: 10 hours

Once you have a .apworld and .yaml, navigate to this Google Sheet that contains all of the puzzle references:

https://docs.google.com/spreadsheets/d/1eFc-khH4InTgSBb59i2g7-Fkp9HLMwrYQwlHs-mSJm4/edit?usp=sharing

Make a copy of the sheet for yourself.

All of the locations in this AP World reference specific puzzles on the "CTC GAS Tracking" and "CTC GAS Leak Tracking" tabs. Navigate to these tabs and expand all of the hidden rows to prepare to play!

## Archipelago Rules
Solving each puzzle (links to the puzzle are provided in the spreadsheet) constitutes a check. The goal is to locate a certain number of "Victory Key" items, and complete the Victory Puzzle. Both of these are listed in the generated YAML for your game.

For this archipelago game, the puzzles are split into multiple regions. Each region has 8 puzzles, for a total of 48 locations.
- Classic Sudoku: These are your classic 9x9 puzzles with no extra rules. This is the only region available at the beginning of the game.
- Summation Sudoku: These puzzles rely on addition to meet a certain clue. E.g. Killer sudoku or Arrow sudoku. 
- Positional Sudoku: These puzzles have additional rules about where certain numbers can be placed. E.g. Thermometer sudoku or Fortress sudoku
- Parity Sudoku: These puzzles rely on some kind of A-or-B type parity to be solved. E.g. Kropki sudoku or Even/Odd sudoku
- Variant Sudoku: These puzzles have unique rules or are significant variations on existing rulesets, and are often one-of-a-kind.
- Multi-Rule Sudoku: These puzzles have two or more rules applied at once.

All of the variant regions must be unlocked by finding their respective Key item.

## Other items
### Useful items
Reveal Puzzle Average Time: This box allows you to click the "show time" checkmark in the spreadsheet, revealing the average time taken on a puzzle. This can help guide you toward completing easier puzzles first.

Puzzle Skip: This allows you to skip a particularly difficult puzzle and receive its check regardless. Puzzle skips cannot be used on the Victory Gauntlet.

### Traps
Extra Puzzle: You may get assigned an extra puzzle. Once you finish your current puzzle, you must complete any assigned trap puzzles before you can move on to your next check puzzle. Puzzle Skips can be used to negate a trap if necessary.

### Filler
Party Hat: Wooo!
