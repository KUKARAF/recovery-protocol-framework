# Recovery Protocol - Platform Documentation

## Overview

A git-based learning and recovery platform where users rebuild their programming capabilities by solving mission-based tasks. The system has two components:

1. **Local CLI Tool** (`resurrection` command) - For local development and validation
2. **Web Service** (hosted) - For remote hosting, SSH key management, progress tracking, and result visualization

Users develop solutions locally, validate with the CLI (works like a pre-commit hook), then push to the service for integration and tracking.

## Core Concept

- **Narrative**: An AI system recovering from catastrophic failure, rebuilding capabilities one mission at a time
- **Missions**: Core programming capabilities (data structures, I/O, algorithms, concurrency, etc.)
- **Tasks**: Specific learning challenges within each mission
- **Verification**: Pytest-based automated testing for each task
- **Validation**: Same test runner locally (CLI) and remotely (service)
- **Tracking**: Progress persisted in git commits and dashboard

## Architecture

```
recovery-protocol/
├── CLAUDE.md                    # This file
├── backstory.md                 # Platform narrative
├── character.md                 # System profile
├── pyproject.toml               # uv configuration
│
├── src/resurrection/            # Local CLI tool (uv installable)
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point (validate, status)
│   ├── validator.py             # Test runner (pytest integration)
│   ├── progress.py              # Local progress tracking
│   └── tui/
│       ├── __init__.py
│       └── display.py           # Result formatting
│
├── missions/                    # Task structure (users clone/push this)
│   ├── mission_1_data_basics/
│   │   ├── task_1.py            # User edits these
│   │   ├── task_2.py
│   │   └── tests/
│   │       ├── test_task_1.py
│   │       └── test_task_2.py
│   ├── mission_2_io_parsing/
│   └── ... (missions 3-5)
│
└── web-service/                 # Hosted service (separate repo)
    ├── app.py                   # Web UI and git handler
    ├── ssh_handler.py           # SSH key management
    ├── git_receiver.py          # Post-receive hook
    ├── validator.py             # Runs pytest on push
    └── dashboard.py             # Progress visualization
```

## User Workflow

1. **Setup**
   - Add SSH key to web service
   - Clone recovery repository
   - Set up local environment with `uv sync`

2. **Local Development**
   - Edit task files in `missions/mission_X/task_Y.py`
   - Run `resurrection validate` to test locally
   - Same tests run locally as on the server

3. **Commit & Push**
   - `git commit` (optionally with pre-commit hook using `resurrection validate`)
   - `git push` to recovery service
   - Server runs validation automatically
   - Results appear in web dashboard

4. **Progress Tracking**
   - Web dashboard shows mission/task progress
   - Local progress saved in git history
   - Commits are timestamped proof of learning

## Mission Progression

**Mission 1: Data Manipulation Foundations**
- List operations, sorting, string parsing, filtering
- Building blocks: understand data transformation
- Core skill: breaking problems into data-flow steps

**Mission 2: I/O and Parsing** (Coming)
- File operations, regex, log parsing, text processing
- Core skill: reading the world, extracting meaning

**Mission 3: Search and Structure** (Coming)
- Data structure design, searching, graph basics
- Core skill: organizing information efficiently

**Mission 4: Functions and Recursion** (Coming)
- Function design, recursion, divide-and-conquer
- Core skill: problem decomposition

**Mission 5: Concurrency and Systems** (Coming)
- Threading, multiprocessing, async/await
- Core skill: managing complexity at scale

## Local CLI Tool

### Installation
```bash
uv pip install -e .
# Or: uv sync
```

### Commands
```bash
resurrection validate              # Run all mission tests
resurrection validate --mission 1  # Run specific mission
resurrection status               # Show progress
```

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/sh
resurrection validate || exit 1
```

The CLI uses the same validator as the web service, ensuring local and remote tests are identical.

## Test Design

Each task has 15-20 comprehensive tests covering:
- **Normal cases** - Happy path, typical inputs
- **Edge cases** - Empty, single, boundary conditions
- **Type handling** - Mixed types, None values
- **Performance** - Timing requirements for algorithmic efficiency
- **Properties** - Order preservation, immutability requirements

Tests are the specification. Code passes when it satisfies all tests.

## Technology Stack

- **Language**: Python 3.11+
- **Package Manager**: uv (fast, dependency-free)
- **Testing**: pytest (comprehensive, extensible)
- **CLI Framework**: Typer
- **Display**: Rich (with Textual upgrade planned)
- **Web Framework**: FastAPI or Flask (for service)
- **Git Integration**: Gitea or custom hooks

## Key Design Principles

1. **Narrative-Driven** - Every task has context tying to AI system recovery
2. **Test-First** - Tests are the specification, code satisfies tests
3. **Local-First** - Develop and validate locally before pushing
4. **Transparent** - Same validator locally and remotely
5. **Progressive** - Missions build on prior knowledge
6. **Skill-Focused** - Each mission teaches real engineering capability

## What This Is NOT

- Not a game (no points, levels, or competition)
- Not a tutorial (you write the code, not reading code)
- Not a course (self-directed learning, not curriculum)
- Not a judge (tests are just verification, not judgment)

## What This IS

- A structured learning environment
- A validation and progress tracking system
- A commitment mechanism (git history proves learning)
- A capability rebuilding metaphor for skill development

## Future Enhancements

- Textual UI for richer terminal experience
- Web dashboard with progress visualization
- Peer code review system
- Bonus challenge variants
- Leaderboard (optional, opt-in)
- Community submission showcase
