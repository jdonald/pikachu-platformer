# pikachu-platformer

Sample Vibe-coded platformer on pygame-zero, runs on Raspberry Pi 4

## Gameplay

This is a simple Mario-like game in pygame-zero. The character motion can be controlled via WASD (or basically just A and D for left and right), or arrow keys for the same. Spacebar to jump.

The character is displayed as a Pikachu, but acts more like Mario. There are 10 levels that contain Mario-like platforms, but simple enough that there are no breakable bricks or coin blocks. Platform levels are procedurally generated with a fixed seed. 10 levels side-scrolling, and when Pikachu gets to the end the level is complete. The only enemies are walking Eevee characters who behave more like Goombas and can be stomped, but if Pikachu touches them from the side, must restart the level. Infinite lives.

## Requirements

TODO: text needed here to recommend for Raspberry Pi 4+ with Raspberry Pi OS, but this should run on other targets that support Python3 (macOS, Linux, Windows).

## Running

Include instructions here for setting up Python virtualenv with pygame-zero and any other pip dependencies.
