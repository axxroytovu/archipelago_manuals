# Using Events in Manual

## What are events? Why is this useful?

Archipelago is full of items, but there are ways to use fake events and items to influence logic. These are called events.

If you have particularly complicated logic for a specific location, you can reference events which have their own logic.

As an example, you may have a location that requires you to collect 10 shards from across the map. Each of those shards could send a normal archipelago item, as well as have an "event_shard" that tells the logic that you could reach that location. Then you can add a second location that requires 10 "event_shard" items.

## Add the events

Events are added in `after_create_regions`. You are essentially adding locations and items with `Null` as the ID.

```py
def after_create_regions(world: World, multiworld: MultiWorld, player: int):

    events = {
        "event_location_1": {"item": "event Item", "region": "region name"}, # This dictionary defines all of your events
        ...
    }

    for e_name, definition in events.items(): # loop through the events
        e_region = multiworld.get_region(definition["region"], player) # get the region specified
        e_item = ManualItem(definition["item"], ItemClassification.progression, None, player=player) # Create the event item
        e_loc = ManualLocation(player, e_name, None, e_region) # create the event location
        e_region.locations.append(e_loc) # put the event location in the region
        e_loc.place_locked_item(e_item) # place the event item at the event location
```

Once you've added the event locations, then you'll need to add logic to them in `after_set_rules`. You can reference the [CollectionState documentation](https://github.com/ArchipelagoMW/Archipelago/blob/6dc461609b1df651e327050f279f8cdce38fe95b/BaseClasses.py#L712) to see what tools are available for logic.

```py
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    events = {
        "event_location_1": lambda state: state.has_all(["item 1", "item 2"], player), # Use lambda functions to define the logic of each event
        ...
    }

    for e_name, rule in events.items(): # loop through the events
        e_loc = multiworld.get_location(e_name, player)
        e_loc.access_rule = rule
```

**NOTE**: There is a bug in Manual that messes with this logic slightly. You'll need to apply [this fix](https://github.com/ManualForArchipelago/Manual/pull/140/files).

After you define all of your events, you can add this simple function to `hooks/Rules.py` to reference events in your logic.

```py
def Event(world: World, multiworld: MultiWorld, state: CollectionState, player: int, event_name: str, count: str = "1"):
    return state.has(event_name, player, int(count))
```

Then in a location, you reference events as such:
```json
{
    "name": "Location Name",
    "category": ["Category"],
    "region": "Ranch",
    "requires": "{Event(event Item 1)} and {Event(event Item 2, 3)}"
}
```
