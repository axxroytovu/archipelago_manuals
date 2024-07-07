# Object classes from AP that represent different types of options that you can create
from Options import FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
class Victory(Choice):
    """Choose the victory condition"""
    display_name = "The final victory quest"
    option_high_rank = 1
    option_master_rank = 2
    option_low_rank = 0
    default = 2

class ShufflePost(Toggle):
    """Shuffle quests that usually would only be available after the victory location is found"""
    display_name = "Suffle post-game quests"

class QuestDensity(Choice):
    """Modifies the number of quests you need to complete"""
    display_name = "Quest density"
    option_reduced = 0
    option_normal = 1
    option_insane = 2
    default = 1

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["victory_condition"] = Victory
    options["shuffle_postgame"] = ShufflePost
    options["quest_density"] = QuestDensity
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    return options