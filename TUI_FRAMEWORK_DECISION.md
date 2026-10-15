# TUI Framework Decision: Textual for Resurrection Protocol

## Research Summary (Completed by Research Agent)

After comprehensive evaluation of Rich, Textual, Blessed, Curses, and Typer frameworks, **Textual 8.2.8+** is the clear winner for Resurrection Protocol.

## Why Textual Wins

### 1. **Interactive Game UI**
- 30+ built-in widgets (DataTable, TextArea, Button, Custom, etc.)
- Reactive properties (UI auto-updates when data changes)
- Not just static output like Rich

### 2. **Native Syntax Highlighting**
- Pygments integration built-in
- 598+ programming languages supported
- Theme support: monokai, vim, solarized, dracula, etc.
- Perfect for displaying player code solutions

### 3. **Smooth Animations**
- Full easing system (30+ functions)
- in_out_cubic, out_back, out_elastic for satisfying feedback
- Challenge completion animations match Zachatronics style
- Slide, fade, scale effects built-in

### 4. **CSS-Like Styling**
- `.tcss` stylesheet files for Zachatronics aesthetic
- Monospace terminal fonts, dark backgrounds, bright accents
- TIS-100 green, EXAPUNKS amber, Opus Magnum gold themes possible
- Box-drawing characters ▌░█╔═╗ etc. built-in

### 5. **Testing Support**
- Pilot for unit testing game logic without terminal
- Can test reactive components programmatically

### 6. **Active Maintenance**
- 37.5k+ stars on GitHub
- Very active development, regular updates
- Excellent documentation with examples

## Why NOT Others

| Framework | Why Not |
|-----------|---------|
| **Rich** | Static output only, can't handle interactive gameplay |
| **Blessed** | Too low-level, 10x boilerplate for simple tasks |
| **Curses** | Ancient API, verbose, hard to animate |
| **Typer+Rich** | CLI-only, not designed for games |

## Proposed Architecture

```
src/resurrection/tui/
├── app.py                 # Textual App subclass
├── widgets/
│   ├── code_viewer.py    # Syntax-highlighted code display
│   ├── scoring.py        # Correctness/Efficiency/Elegance bars
│   ├── progress.py       # Challenge progress animation
│   ├── metrics.py        # Time/memory display
│   └── challenge_panel.py # Instructions & brief
├── styles/
│   ├── default.tcss      # Main stylesheet
│   ├── zachatronics.tcss # Retro-futuristic theme
│   └── themes.py         # Color palette definitions
└── game_screen.py        # Main game layout orchestration
```

## Color Palettes (Zachatronics-Inspired)

### TIS-100 Style (Green Terminal)
```
Primary: #00FF00 (bright green)
Background: #001100 (dark green)
Accent: #00CC00 (medium green)
Error: #FF0000 (bright red)
```

### EXAPUNKS Style (Amber CRT)
```
Primary: #FFAA00 (amber)
Background: #1A1410 (dark brown)
Accent: #FF8800 (orange)
Success: #00FF00 (lime green)
```

### Opus Magnum Style (Gold/Purple)
```
Primary: #FFD700 (gold)
Background: #1A1a2e (very dark blue)
Accent: #9d4edd (purple)
Secondary: #00d4ff (cyan)
```

## Components We'll Build

### CodeViewer Widget
- Displays player's solution code
- Syntax highlighting via Pygments
- Line numbers
- Read-only or edit mode
- Scrollable for long solutions

### ScoringDisplay Widget
- Progress bars for Correctness, Efficiency, Elegance
- Animated fill-up on completion
- Score percentage text
- Color changes: red→yellow→green as score improves

### ProgressIndicator Widget
- Shows challenges 1-5 as boxes
- Completed: ✓ (green)
- Current: ► (pulsing highlight)
- Locked: ○ (gray)
- Animated transition between challenges

### MetricsDisplay Widget
- Execution time: "Took 45ms"
- Memory used: "1.2 MB"
- Algorithm complexity rating
- Performance badges

### ResultsScreen
- Challenge brief (top panel)
- Player code (left panel)
- Test results (right panel)
- Scoring breakdown (bottom)
- Smooth transitions between challenges

## Implementation Timeline

1. **Phase 1** (Now): Update pyproject.toml, add Textual to deps
2. **Phase 2**: Build CodeViewer widget (syntax highlighting)
3. **Phase 3**: Reactive ScoringDisplay (auto-updating)
4. **Phase 4**: Animation system (challenge transitions)
5. **Phase 5**: Full game layout with all widgets
6. **Phase 6**: Integrate with game loop

## Dependencies to Add

```
textual==8.2.8       # Full TUI framework
pygments==2.13.0     # Code syntax highlighting
```

Update `pyproject.toml`:
```toml
dependencies = [
    "rich>=15.0.0",
    "textual>=8.2.8",
    "pygments>=2.13.0",
    "typer>=0.27.3",
]
```

## Getting Started with Textual

### Basic App Structure
```python
from textual.app import ComposeResult, RenderableType
from textual.containers import Container, Vertical
from textual.widgets import Static, Header, Footer

class ResurrectionApp(TextualApp):
    CSS = """
    Screen {
        layout: vertical;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield ChallengePanel()
        yield CodeViewer()
        yield ScoringDisplay()
        yield Footer()
```

### Reactive Properties
```python
class ScoringDisplay(Static):
    score: Reactive[int] = Reactive(0)
    
    def watch_score(self, old_score: int, new_score: int) -> None:
        # Automatically called when score changes
        self.update(f"Score: {new_score}%")
```

### Animations
```python
async def animate_completion(self):
    await self.animate("offset_x", 100, duration=0.5, easing="out_cubic")
```

## Next Steps

1. Install Textual: `uv add textual pygments`
2. Scaffold the game app structure
3. Build CodeViewer widget first (core component)
4. Test syntax highlighting with sample code
5. Build ScoringDisplay with reactive updates
6. Integrate with game loop

---

**Status**: Ready to implement. Textual provides everything needed for a polished, Zachatronics-worthy experience with minimal code.
