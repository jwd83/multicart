# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

JackGames Multicart is a PyGame-based collection of games built for a nephew named Jack. The project features multiple mini-games in a single executable, supporting both desktop (Windows/Linux/macOS) and web browsers via PyGame CE and pygbag.

## Key Architecture Components

### Scene-Based Architecture
The game uses a scene stack system where scenes are managed by the `Game` class:
- **Scene Stack**: Scenes can be pushed, popped, or replaced using `game.scene_push`, `game.scene_pop`, `game.scene_replace`
- **Scene Base Class**: All scenes inherit from `Scene` class in `scene.py` which provides common functionality
- **Scene Loading**: Scenes are dynamically loaded using `eval("scenes." + scene_name + "(self)")` pattern

### Core Classes
- **Game**: Main game loop, input handling, scene management, and configuration
- **Scene**: Base class for all game scenes with drawing utilities, text rendering, and sound management
- **FastText**: Optimized text rendering system that only re-renders when text changes
- **Button**: UI button class with hover and click states
- **SpriteSheet**: Utility for managing sprite sheet assets

### Settings System
The project uses multiple settings files that are swapped during build:
- `settings.py` - Current active settings (never edit directly)
- `settings-win.py` - Desktop/Windows settings
- `settings-wasm.py` - Web browser settings via pygbag

## Common Development Commands

### Running the Game
```bash
# Run the main game
python main.py

# Run with specific scene (for debugging)
python main.py scene run <SceneName>
```

### Scene Management
```bash
# Create a new scene
python main.py scene new

# List all available scenes
python main.py scene list
```

### Building for Different Platforms
```bash
# Build Windows executable
build-win.bat

# Build for web browsers
build-web.bat
```

### Color Palette Swapping (Swappy Tool)
```bash
# Generate color palette CSV from image folder
python swappy.py <source_folder> <output.csv>

# Apply palette swap using CSV
python swappy.py <source_folder> <palette.csv> <target_folder>
```

### FastAPI Server (QuadBlox multiplayer)
```bash
# Run the multiplayer game server
python qbfastapi.py

# Server runs on port 8000 by default, or PORT environment variable
```

## Development Patterns

### Adding New Games/Scenes
1. Create scene using `python main.py scene new`
2. Implement `update()` and `draw()` methods
3. Scene is automatically imported in `scenes/__init__.py`
4. Add to game selection logic as needed

### Input Handling
- `game.pressed` - Current key states
- `game.just_pressed` - Keys pressed this frame
- `game.just_released` - Keys released this frame
- `game.just_mouse_down/up` - Mouse button events

### Asset Loading
- Images: `self.load_png("filename.png")` returns image and rect
- Sounds: Automatically loaded from `assets/sounds/` into `game.sfx` dict
- Music: `self.play_music("path/in/assets")`

### Text Rendering
- Quick text: `self.standard_text("Hello")` using scene defaults
- Custom text: `self.make_text(text, color, fontSize, font, stroke options)`
- Dynamic text: `self.Text("Hello", (x,y), anchor)` returns FastText object

### Console System
- Press backtick (`) to open/close console
- Add commands to scenes via `self.commands` dict
- Console provides logging and debugging capabilities

## Build System Notes

### Font Requirements
- Upheaval font looks best at multiples of 20px
- Default fonts: `upheavtt.ttf` (main), `TeenyTinyPixls-o2zo.ttf` (small)

### Multi-Platform Considerations
- Build scripts swap settings files automatically
- PyInstaller used for Windows builds
- pygbag used for web builds
- Assets folder must be copied to distribution

### Performance
- 640x360 resolution (16:9 aspect ratio)
- 60 FPS target
- Built-in performance monitoring in debug mode
- Frame load percentage displayed when `DEBUG = True`

## Server Deployment

The QuadBlox multiplayer game includes a FastAPI server that can be deployed to fly.io or Railway:
- PostgreSQL database required for leaderboards
- Environment variable `DATABASE` for connection string
- Environment variable `PORT` for server port (defaults to 8000)

## Asset Credits

The project includes assets from multiple sources including DaFluffyPotato, Kenney.nl, itch.io creators, OpenGameArt, and AI-generated content. See README.md for full attribution.