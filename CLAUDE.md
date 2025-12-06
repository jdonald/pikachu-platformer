# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A simple Mario-like platformer game built with pygame-zero, designed to run on Raspberry Pi 4+. The player controls Pikachu through 10 procedurally-generated side-scrolling levels with platforms and walking Eevee enemies (Goomba-like behavior).

## Key Game Design

- **Controls**: WASD or arrow keys for movement, Spacebar to jump
- **Character**: Pikachu sprite with Mario-like physics
- **Levels**: 10 procedurally-generated levels with fixed seed
- **Enemies**: Eevee characters that walk and can be stomped from above; touching from the side restarts level
- **Lives**: Infinite
- **Platforms**: Simple static platforms (no breakable bricks or coin blocks)

## Development Commands

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python3 pikachu_platformer.py
# or
pgzrun pikachu_platformer.py

# Syntax check
python3 -m py_compile pikachu_platformer.py
```

## Code Architecture

The game is implemented in a single file `pikachu_platformer.py` using pygame-zero:

- **Player class**: Handles Pikachu movement, jumping (JUMP_SPEED = -12), and physics (GRAVITY = 0.5)
- **Enemy class**: Manages Eevee walking behavior with edge detection and direction reversal
- **Platform class**: Static rectangular platforms with collision boundaries
- **LevelGoal class**: End-of-level trigger positioned at x=4800
- **generate_level()**: Procedural generation using `random.seed(level_num * 42)` for reproducible levels
- **Camera system**: `camera_x` follows player at WIDTH//3 offset for side-scrolling
- **Game states**: PLAYING, LEVEL_COMPLETE, RESTARTING (using Enum)

### Collision Detection

- Platform collision: Checks player's old_y position to determine if landing on top vs hitting from side
- Enemy collision: Stomping detected when player.vel_y > 0 and coming from above; side collision triggers level restart
- Goal collision: Triggers level completion when player rect intersects goal rect

### Level Design

- Each level is 5000 pixels wide with procedurally placed platforms
- Number of platforms scales with level: `8 + level_num * 2`
- Number of enemies scales with level: `3 + level_num`
- Ground platform spans full width at y = HEIGHT - 100
