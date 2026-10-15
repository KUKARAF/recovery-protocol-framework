# Resurrection Protocol - Quick Start Guide

## What We Built

A Zachatronics-inspired programming challenge game set in the Illuminae Files universe with:

✅ **5 complete challenges in Chapter 1** (Signal Recovery)
✅ **Editable challenge files** - open in vim, nano, or your editor
✅ **Comprehensive test suites** - 12-20 tests per challenge
✅ **Game framework** - installable Python package via uv
✅ **Rich TUI** - beautiful terminal display
✅ **Project documentation** - backstory, character, CLAUDE.md

## File Structure Created

```
python_game/
├── README.md                          # How to play
├── QUICKSTART.md                      # This file
├── CLAUDE.md                          # Project overview
├── TUI_FRAMEWORK_DECISION.md          # Textual research & recommendations
├── backstory.md                       # Game narrative
├── character.md                       # Your hacker character
├── pyproject.toml                     # uv configuration
│
├── src/resurrection/                  # Main package
│   ├── __init__.py
│   ├── cli.py                         # CLI entry point
│   ├── game.py                        # Game orchestration
│   ├── evaluator.py                   # Pytest integration
│   ├── progress.py                    # Progress tracking
│   └── tui/
│       ├── __init__.py
│       └── display.py                 # Rich-based UI
│
└── chapters/
    └── chapter_1/                     # COMPLETE
        ├── metadata.json              # Chapter definition
        ├── challenges/
        │   ├── sort_signals.py        # Challenge 1.1
        │   ├── extract_callsign.py    # Challenge 1.2
        │   ├── decode_status.py       # Challenge 1.3
        │   ├── filter_logs.py         # Challenge 1.4
        │   └── merge_signals.py       # Challenge 1.5
        └── tests/
            ├── test_sort_signals.py
            ├── test_extract_callsign.py
            ├── test_decode_status.py
            ├── test_filter_logs.py
            └── test_merge_signals.py
```

## Chapter 1: Signal Recovery - The 5 Challenges

All designed to build **fundamental data manipulation skills**:

### 1. **Sort Signals** (sort_signals.py)
- **Task**: Sort a list of packet IDs
- **Skills**: List operations, Python sorting, algorithm understanding
- **Story**: Restore AIDAN's fragmented transmission order
- **Tests**: 19 test cases (including performance: <100ms for 1000 items)

### 2. **Extract Callsigns** (extract_callsign.py)
- **Task**: Find valid operator callsigns (uppercase, 3-15 chars) in corrupted data
- **Skills**: String parsing, character validation, pattern recognition
- **Story**: Recover last known operator identities from contact logs
- **Tests**: 18 test cases (edge cases, length boundaries)

### 3. **Decode Status** (decode_status.py)
- **Task**: Count satellite status codes (S/O/F/U) from a string
- **Skills**: Dictionary aggregation, O(n) algorithm design
- **Story**: Assess Grid satellite health for recovery prioritization
- **Tests**: 15 test cases (ignoring invalid chars, large counts)

### 4. **Filter Logs** (filter_logs.py)
- **Task**: Extract error messages ([ERR] prefix) from mixed logs
- **Skills**: List filtering, list comprehensions, string cleanup
- **Story**: Extract error traces for crash analysis
- **Tests**: 18 test cases (case sensitivity, prefix removal)

### 5. **Merge Signals** (merge_signals.py)
- **Task**: Merge two equal-length lists by alternating: A[0], B[0], A[1], B[1]...
- **Skills**: List iteration, algorithm design, data combination
- **Story**: Recover dual-redundancy channel from parallel transmission
- **Tests**: 18 test cases (order preservation, large lists)

## Getting Started

### 1. Install & Setup

```bash
cd /var/home/rafa/dev/python_game

# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### 2. Understand the Story

Read the backstory to get immersed:
```bash
cat backstory.md    # The world and mission
cat character.md    # Who you are: GHOST_PROTOCOL
cat CLAUDE.md       # Technical project overview
```

### 3. Start Playing

```bash
# Launch the game
resurrection
```

This will:
- Show Chapter 1 brief
- Display first challenge
- Tell you which file to edit

### 4. Solve a Challenge

```bash
# Open the challenge in your editor
vim chapters/chapter_1/challenges/sort_signals.py

# Read the docstring and implement the function
# Save your solution
```

### 5. Test Manually (Optional)

```bash
# Run tests for one challenge
python -m pytest chapters/chapter_1/tests/test_sort_signals.py -v

# Run all Chapter 1 tests
python -m pytest chapters/chapter_1/tests/ -v

# Run with verbose output
python -m pytest chapters/chapter_1/tests/test_sort_signals.py -vv
```

### 6. Check Progress

```bash
resurrection status
```

Shows all completed challenges.

## Design Philosophy

Each challenge is crafted with:

1. **Real Engineering Skills** - Not just puzzles, but actual programming fundamentals
2. **Compelling Narrative** - Every task has a mission context in the Illuminae universe
3. **Comprehensive Testing** - Edge cases, performance, type handling all covered
4. **Clear Learning Goals** - Each challenge teaches specific concepts

**Example**: Sort Signals teaches:
- List operations (accessing, iterating, modifying)
- Python's built-in sorting (sorted() vs list.sort())
- Algorithm complexity awareness (why O(n log n) is efficient)
- Testing edge cases (empty lists, duplicates, negatives)
- All while rebuilding Earth's defense grid in-universe

## Test Design

Tests follow this pattern:
- **Normal cases** - happy path, typical inputs
- **Edge cases** - empty, single element, boundaries
- **Type handling** - mixed types, None, booleans
- **Performance** - timing checks for large datasets
- **Properties** - verify invariants (order preserved, no mutations)

Example `test_sort_signals.py`:
- `test_simple_positive_numbers()` - basic sorting
- `test_reverse_sorted()` - reverse input
- `test_mixed_positive_and_negative()` - mixed sign numbers
- `test_performance_1000_elements()` - 1000 items in <100ms
- `test_returns_new_list()` - not mutating original

**Every challenge has 15-20 tests covering realistic scenarios.**

## Future Chapters (Scaffolded)

Directories exist for Chapters 2-5. When ready, add:
1. Challenge files in `challenges/`
2. Test files in `tests/`
3. Update `metadata.json`

```
Chapter 2: Channel Reopening     - File I/O, regex, log parsing
Chapter 3: Network Mapping       - Data structures, searching, sets
Chapter 4: Algorithm Reconstruction - Recursion, dynamic programming
Chapter 5: Distributed Defense   - Threading, multiprocessing, concurrency
```

## Technology Stack

- **Language**: Python 3.11+
- **Package Manager**: uv (ultra-fast, dependency-free)
- **Testing**: pytest (comprehensive test framework)
- **TUI Framework**: Rich (current) → Textual (planned upgrade)
- **Syntax Highlighting**: Pygments (for code display)
- **CLI**: Typer (command-line interface)

## Key Features

### Editable Challenges ✏️
- Challenge files are plain Python with docstrings
- Edit in vim, nano, VS Code, or any text editor
- Game tells you the exact file path

### Automated Grading ✅
- pytest tests run automatically
- Comprehensive coverage (15-20 tests per challenge)
- Clear pass/fail feedback
- Performance requirements checked

### Progress Tracking 📊
- `~/.resurrection_progress.json` stores completions
- `resurrection status` shows your progress
- Ready for future leaderboard/scoring features

### Framework Integration 🎮
- Game logic in `src/resurrection/`
- Installable as Python package (`uv pip install -e .`)
- CLI commands: `resurrection`, `resurrection test`, `resurrection status`
- Clean separation of concerns

## Troubleshooting

### Tests won't import the challenges
```bash
# Make sure you're in the right directory
cd /var/home/rafa/dev/python_game

# Reinstall the package
uv pip install -e .

# Or resync everything
uv sync --force
```

### Pytest not found
```bash
source .venv/bin/activate
uv pip install pytest --force-reinstall
```

### Original list modified (sort_signals)
This is intentional testing! The function should use `sorted()` (returns new list) not `list.sort()` (modifies in place). Tests verify this understanding.

## Next Steps

1. ✅ Read backstory.md and character.md (get immersed)
2. ✅ Run `resurrection` and solve sort_signals
3. ✅ Solve all 5 Chapter 1 challenges
4. ⏳ Check back for Chapter 2: Channel Reopening (coming soon)

---

## Architecture Notes for Developers

### Game Loop
1. `cli.py` parses commands and launches game
2. `game.py` loads chapter metadata, shows intro, presents challenges
3. Player edits challenge file in external editor
4. `evaluator.py` runs pytest on challenge tests
5. `tui/display.py` renders results with Rich panels
6. `progress.py` saves completion to JSON

### Challenge Structure
Each challenge:
- Has a docstring with mission brief (Illuminae narrative)
- Includes type hints and complexity notation
- Provides example inputs/outputs
- Is backed by 15-20 comprehensive tests
- Tests cover normal, edge, and performance cases

### Testing Philosophy
- **TDD**: Tests written first, challenges written second
- **Comprehensive**: Edge cases, boundaries, type handling
- **Real-world**: Performance requirements (e.g., <100ms)
- **Educational**: Tests teach expected behavior

---

**You're not just solving puzzles. You're rebuilding Earth's defenses.**

**Welcome to the Resurrection Protocol.**

**Time to code.**
