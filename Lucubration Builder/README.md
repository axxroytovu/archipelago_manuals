# Lucubration Builder

## What is this?

Lucubration or Tasks manuals are a way to do real-life tasks integrated with Archipelago. This python script is a way to quickly build a customized tasks manual with functioning logic without the hassle of doing it manually. The included `tasks.yaml` file includes a sample set of tasks.

## How to use

1. Download the latest stable manual `.apworld` from https://github.com/ManualForArchipelago/Manual/releases
2. Download the two files attached to this release.
3. Put all three files in the same folder
4. Modify the `tasks.yaml` file as much as you want to customize your experience
5. Run the python script
6. Use the generated `.apworld` and `.yaml` files!

## Format for `tasks.yaml`

### Meta

- `player_name`: your name
- `traps`: functionality coming soon
- `checks_per_hour`: This is used in the calculation for how many checks to include for durated tasks. If you have 4 checks per hour, and you say you want to spend 2 hours on a task, the script will create 8 locations. 

### Tasks

There are 5 types of tasks

#### `book`

Read a book or progress through a numbered sequence of tasks. Each chapter is 1 location, and each progressive item unlocks 2 chapters.

```
- type: book
  name: The Bible
  start_chapter: 1
  end_chapter: 31
  category: Reading
```

- `name`: The name of the book you want to read
- `start_chapter` and `end_chapter`: define the range of chapters you want to read. `start_chapter` is optional and will default to 1.
- `category`: optional, defines a category to assign to the locations & items. Defaults to "Reading"
- `starting`: optional, allow the player to start with this task

#### `practice-general`

Practice a general task or skill. Each progressive item unlocks 2 sequential items

```
- name: German
  type: practice-general
  category: "Language Practice"
  hours: 5
  starting: true
- name: Korean
  type: practice-general
  category: "Language Practice"
  checks: 10
```

- `name`: the name of the task you want to practice
- `hours` or `checks`: define the duration of the practice. Hours will use the meta `checks_per_hour` to define the number of locations. Checks directly defines the number of locations.
- `category`: optional, defines a category to assign to the locations & items. Defaults to "Practice"
- `starting`: optional, allow the player to start with this task

#### `practice-specific`

Practice a task using a series of more specific objectives. Each specific objective will have its own progressive unlock items in the multiworld, and 

```
- name: Guitar
  type: practice-specific
  category: "Music"
  hours_per_item: 1
  items:
  - All You Need Is Love
  - Across the Universe
  - Good Day Sunshine
  - Help!
  - Hey Jude
- name: Pixel Art
  type: practice-specific
  category: "Art"
  checks_per_item: 2
  items:
  - Mario
  - Luigi
  - Bowser
  - Peach
```

- `name`: the category of task you want to practice
- `hours_per_item` or `checks_per_item`: defines the duration of practice for each task. Hours will use the meta `checks_per_hour` to define the number of locations. Checks directly defines the number of locations. 
- `items`: A list of the specific tasks to perform. Each item will have its own progressive item.
- `category`: optional, defines a category to assign to the locations & items. Defaults to "Workout"
- `starting`: optional, allow the player to start with this task

#### `workout`

Perform a repeating set of the same tasks multiple times. Each progressive item unlocks 1 repetition of the tasks. 

```
- name: Daily Workout
  type: workout
  category: "Daily Workout"
  sets:
  - 10 Pushups
  - 10 Situps
  - Half Mile Run
  repetitions: 7
```

- `name`: the name of the task you want to do
- `sets`: a list of the tasks to repeat
- `repetitions`: how many times to repeat the tasks
- `category`: optional, defines a category to assign to the locations & items. Defaults to "Workout"
- `starting`: optional, allow the player to start with this task

#### `tied-projects`

Perform multiple tasks using the same progression items. Each progressive item unlocks a variable number of tasks based on how the projects line up.

```
- name: Knitting Projects
  type: tied-projects
  category: "Knitting"
  projects:
  - name: Knit Hat
    hours: 3
  - name: Knit Socks
    checks: 7
  - name: Knit Sweater
    hours: 10
```

- `name`: the name of the task you want to do
- `projects`: A list of the projects you want to do
  - `name`: The project name
  - `hours` or `checks`: define the duration of the task. Hours will use the meta `checks_per_hour` to define the number of locations. Checks directly defines the number of locations.
- `category`: optional, defines a category to assign to the locations & items. Defaults to "Projects"
- `starting`: optional, allow the player to start with this task
