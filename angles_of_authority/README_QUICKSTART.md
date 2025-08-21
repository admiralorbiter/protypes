# Angles of Authority - Quick Start Guide

## Getting Started (5 minutes)

This guide will get you from zero to a running test scene in under 5 minutes.

### Prerequisites
- Python 3.11 or higher
- Git (to clone the repository)

### Step 1: Setup Environment
```bash
# Navigate to the project directory
cd angles_of_authority

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Run the Game
```bash
# Option 1: Use the run script (recommended)
python run.py

# Option 2: Run directly
python main.py
```

### What You Should See
- A dark blue window with "Test Scene" text
- A counter that increments each frame
- Control instructions displayed on screen
- Console output when you press action keys (R, V, F)

### Controls (Test Scene)
- **WASD**: Movement (not yet implemented)
- **1/2**: Select operator (not yet implemented)
- **R**: Toggle ROE (prints to console)
- **V**: Shout action (prints to console)
- **F**: Flashbang action (prints to console)
- **Space**: Pause/Unpause
- **Escape**: Quit game

### Troubleshooting

**"Module not found" errors:**
- Make sure you're in the `angles_of_authority` directory
- Ensure virtual environment is activated
- Try running `python run.py` instead of `python main.py`

**Pygame installation issues:**
- On Windows: `pip install pygame --pre` (for latest version)
- On macOS: `brew install pkg-config` then `pip install pygame`

**Display issues:**
- Try running with `SDL_VIDEODRIVER=x11 python main.py` on Linux
- Check that your graphics drivers are up to date

### Next Steps

Once the test scene is running successfully:

1. **Review the code structure** in `core/` and `scenes/`
2. **Check the development plan** in `DEVELOPMENT_PLAN.md`
3. **Start implementing Phase 1** - Core systems and basic movement

### Development Workflow

1. **Test your changes**: Run `python run.py` after each major change
2. **Check the console**: Look for error messages and debug output
3. **Use the test scene**: Add new features to `TestScene` first, then move to proper scenes
4. **Follow the phases**: Stick to the development plan to avoid getting overwhelmed

### Need Help?

- Check the main `readme.md` for game design details
- Review `DEVELOPMENT_PLAN.md` for implementation roadmap
- Look at the console output for error messages
- The test scene is designed to help debug basic issues

---

**Happy coding!** 🎮
