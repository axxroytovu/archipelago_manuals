# Fighting Game Builder

## What is this?

Lots of 1v1 online games can use a uniform or consistent structure to integrate with Archipelago manual. This script quickly builds the .apworld based on a provided setup .yaml file.

## How to use

1. Download the latest manual `.apworld` from https://github.com/ManualForArchipelago/Manual/releases. **THIS SCRIPT REQUIRES AT LEAST VERSION UNSTABLE_20240407**
2. Download the files attached to this release.
3. Put all three files in the same folder
4. Modify the `.yaml` files as much as you want to customize your experience or create your own!
5. Run the python script from the command line or by double-clicking
6. Use the generated `.apworld` and `.yaml` files!

## Format for `.yaml` file

### Meta

- `player_name`: Your name or alias
- `game_name`: The name of the game you want to play
- `victory_macguffin_name`: [optional] Gives a specific name to the victory macguffin item
- `starting_characters`: [optional] If this is a list, it will give exactly the listed characters in the starting inventory. If this is an integer, it will give that many random characters in the starting inventory. If this is blank, it will default to 5 random characters (if characters exist for the game).
- `character_alias`: [optional] Allows you to define a different category name for the character items. Defaults to "Character".
- `filler_name`: [optional] Defines the auto-generated filler name. Defaults to "Nothing".

### Characters [optional]

You may optionally define a list of `characters` at the top level. These characters will be applied to all `character-based` game modes. Example:

```
characters:
- Akuma
- Ed
- A.K.I.
- Rashid
- Cammy
- Lily
- Zangief
- JP
...
```

### Game Modes

There are 4 types of game modes. All game mode definitions must have at minimum:

- `name`: The name of the game mode
- `type`: defines the behavior of the game mode, see the options below

Any mode may be defined as the starting game mode with `starting: true`. This will put enough items into the starting inventory to play some of that game mode.

#### `character-based`

These game modes are tied to unlocking specific characters, and then achieving victories with those characters.

- `victory_count`: [optional] Defines how many victories are unlock locations with each character. Defaults to 1
- `match_name`: [optional] Allows you to rename what the locations are. Defaults to "Match"
- `characters`: [optional] Defines a list of the specific characters allowed to use in this game mode. If this overlaps with the meta character list those items will be used. This defaults to the meta character list if not provided.
- `starting_characters`: [optional] behaves the same as the meta `starting_characters` parameter but is specific to the characters created as part of the mode-specific `characters` list

#### `score-based`

These game modes are usually independent of character, and rely instead on reaching some kind of high-score with any of the characters available to you. **NOTE**: there is artificial logic applied to score-based modes to prevent the maximum score from immediately being in logic with no characters. It is expected that you will be able to reach the maximum score out-of-logic without restriction.

- `max_score`: Defines the highest score to include as a location
- `breakpoint`: [optional] Defines the step size between scores. Defaults to 1. 

Examples: 
- Max score 5, breakpoint 1: This will create 5 locations at score 1, 2, 3, 4 and 5
- Max score 10, breakpoint 2: this will create 5 locations at score 2, 4, 6, 8, and 10
- Max score 100, breakpoint 33: this will create 4 locations at score 33, 66, 99, and 100
- Max score 100, breakpoint 34: this will create 3 locations at score 34, 68, and 100

#### `run-based`

These are incremental modes where each received item gives you access to 1 `run` of the mode.

- `run_count`: Defines how many runs to add to the randomizer
- `checks_per_run`: [optional] Defines how many locations to unlock from the completion of each run. Default is 1
- `run_alias`: [optional] Used if you want the "Run" moniker to be something else. So "Challenge" will name the item "One Mode Challenge" instead of "One Mode Run".

#### `story-based`

These game modes are usually a linear story mode where each item unlocks 1 "chapter" of the story. Chapters may have multiple checks per chapter.

- `chapter_count`: Defines the number of chapters to include
- `checks_per_chapter`: [optional] Defines how many locations to create for each chapter. Default is 1
- `chapter_alias`: [optional] Used if you want to the "chapter" moniker to be something else. So using "Stage" will name the item "Progressive Mode Stage" instead of "Progressive Mode Chapter"
