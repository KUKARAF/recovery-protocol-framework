# Resurrection Protocol

A Zachatronics-inspired programming challenge game set in the Illuminae Files universe.

## Setup

```bash
# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## How to Play

### 1. Read the Story
- `backstory.md` - The world you're saving
- `character.md` - Who you are

### 2. Start Chapter 1

```bash
resurrection
```

This launches the game and guides you through Chapter 1: Signal Recovery.

### 3. Solve Each Challenge

For each challenge:
1. Read the mission brief in the terminal
2. Open the challenge file in your editor (vim/nano/code/etc.)
3. Implement the function according to the instructions
4. Save your solution
5. Return to the game and press Enter

For example, to solve the first challenge:
```bash
vim chapters/chapter_1/challenges/sort_signals.py
```

### 4. Test Your Solution

The game will automatically run tests when you're ready. Or manually:

```bash
# Test a specific challenge
python -m pytest chapters/chapter_1/tests/test_sort_signals.py -v

# Test all of Chapter 1
python -m pytest chapters/chapter_1/tests/ -v

# Test with verbose failure info
python -m pytest chapters/chapter_1/tests/test_sort_signals.py -vv
```

## Chapter 1: Signal Recovery

Five challenges focused on **fundamental data manipulation**:

1. **Sort Signals** - Sort a list of packet IDs
2. **Extract Callsigns** - Find valid operator identifiers in corrupted data
3. **Decode Status** - Count satellite status codes
4. **Filter Logs** - Extract error messages from mixed logs
5. **Merge Signals** - Combine two data streams by alternating elements

## Core Skills Progression

The game is designed to build real engineering skills:

**Chapter 1** - Data Manipulation Fundamentals
- List operations and sorting
- String parsing and validation
- Dictionary aggregation
- Filtering and list comprehensions
- List merging and iteration

**Future Chapters** (Coming)
- **Chapter 2** - File I/O and Regex
- **Chapter 3** - Data Structures and Algorithms
- **Chapter 4** - Functions, Recursion, and Design
- **Chapter 5** - Threading and Parallelization

## Project Structure

```
python_game/
├── src/resurrection/           # Main package (installable)
│   ├── cli.py                 # CLI entry point
│   ├── game.py                # Game orchestration
│   ├── evaluator.py           # Challenge testing
│   ├── progress.py            # Progress tracking
│   └── tui/                   # Terminal UI
├── chapters/                  # Challenge content
│   └── chapter_1/
│       ├── challenges/        # Challenge files (edit these!)
│       ├── tests/            # Pytest test files
│       └── metadata.json     # Chapter definition
├── CLAUDE.md                  # Project documentation
├── backstory.md              # Game narrative
├── character.md              # Player character
└── pyproject.toml            # uv project config
```

## Commands

```bash
# Launch the game
resurrection

# Test a challenge manually
resurrection test --chapter 1 --challenge sort_signals

# Check your progress
resurrection status
```

## Design Philosophy

This game teaches **real engineering skills** through:

1. **Problem Decomposition** - Breaking big problems into small solvable pieces
2. **Data Transformation** - Understanding how data flows through systems
3. **Pattern Recognition** - Finding signal in noise
4. **Testing & Verification** - Validating solutions rigorously
5. **Performance Thinking** - Understanding algorithm complexity

Each challenge has:
- **Clear Narrative Context** - Why you're solving this in-universe
- **Specific Learning Goals** - What engineering skill you're building
- **Comprehensive Tests** - Multiple test cases covering edge cases
- **Scalable Difficulty** - Start simple, add complexity
- **Performance Expectations** - Time and space complexity

## Notes for Developers

- Challenges are **editable in any text editor** - full path shown when playing
- Tests use **pytest** - comprehensive edge case coverage
- Game framework is **installable as a Python package** via uv
- TUI display uses **Rich** library for beautiful terminal output
- Future: Textual framework for interactive UI with animations

## Troubleshooting

If you get import errors:
```bash
# Reinstall the package
uv pip install -e .

# Or resync everything
uv sync --force
```

If tests won't run:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall pytest
uv pip install pytest --force-reinstall
```

## Next Steps

1. Solve all Chapter 1 challenges
2. Check your progress: `resurrection status`
3. Wait for Chapter 2: Channel Reopening (coming soon!)

---

**Remember**: You're not just solving puzzles. You're rebuilding Earth's defenses.

Every line of code matters.

**Welcome to the Resurrection Protocol.**
