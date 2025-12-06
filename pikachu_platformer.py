import pgzrun
import pygame
import random
from enum import Enum

# Game constants
WIDTH = 800
HEIGHT = 600
GRAVITY = 0.5
JUMP_SPEED = -12
PLAYER_SPEED = 5
ENEMY_SPEED = 2

# Colors
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 220, 0)
BROWN = (139, 69, 19)
PINK = (255, 182, 193)
GREEN = (0, 200, 0)

class GameState(Enum):
    PLAYING = 1
    LEVEL_COMPLETE = 2
    RESTARTING = 3

# Game state
game_state = GameState.PLAYING
current_level = 1
camera_x = 0
space_was_pressed = False  # Track spacebar state for jump detection

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jumps_used = 0  # Track jumps for double-jump mechanic

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY

        # Apply velocity
        self.x += self.vel_x
        self.y += self.vel_y

        # Safety floor to prevent falling infinitely (collision detection will set on_ground)
        floor_y = HEIGHT - 100 - self.height
        if self.y > floor_y:
            self.y = floor_y
            self.vel_y = 0

    def jump(self):
        # Allow jumping if on ground OR if haven't used both jumps (double-jump)
        if self.jumps_used < 2:
            self.vel_y = JUMP_SPEED
            self.on_ground = False
            self.jumps_used += 1

    def move_left(self):
        self.vel_x = -PLAYER_SPEED

    def move_right(self):
        self.vel_x = PLAYER_SPEED

    def stop_horizontal(self):
        self.vel_x = 0

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vel_x = ENEMY_SPEED
        self.alive = True

    def update(self, platforms):
        if not self.alive:
            return

        self.x += self.vel_x

        # Check if enemy is about to walk off a platform
        enemy_rect = self.get_rect()
        on_platform = False

        for platform in platforms:
            # Check if enemy is standing on this platform
            if (enemy_rect.bottom >= platform.top and
                enemy_rect.bottom <= platform.top + 10 and
                enemy_rect.right > platform.left and
                enemy_rect.left < platform.right):
                on_platform = True
                break

        # Reverse direction if at edge of platform or hitting wall
        if not on_platform:
            self.vel_x = -self.vel_x
            self.x += self.vel_x * 2  # Move back onto platform

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = x
        self.right = x + width
        self.top = y
        self.bottom = y + height

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

class LevelGoal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

def generate_level(level_num):
    """Generate a level with platforms, enemies, and a goal using fixed seed"""
    random.seed(level_num * 42)  # Fixed seed based on level number

    platforms = []
    enemies = []

    # Add ground
    platforms.append(Platform(0, HEIGHT - 100, 5000, 100))

    # Generate platforms
    num_platforms = 8 + level_num * 2
    for i in range(num_platforms):
        x = random.randint(200, 4500)
        y = random.randint(200, HEIGHT - 200)
        width = random.randint(100, 250)
        height = 20
        platforms.append(Platform(x, y, width, height))

    # Generate enemies
    num_enemies = 3 + level_num
    for i in range(num_enemies):
        x = random.randint(300, 4500)
        y = HEIGHT - 100 - 30  # On the ground
        enemies.append(Enemy(x, y))

    # Create goal at the end of the level
    goal = LevelGoal(4800, HEIGHT - 100 - 60)

    return platforms, enemies, goal

# Initialize level
player = Player(100, HEIGHT - 100 - 32)
player.on_ground = True  # Start on ground so player can jump immediately
platforms, enemies, goal = generate_level(current_level)

# Create sprite actors
try:
    pikachu_sprite = Actor('pikachu')
    # Scale the sprite to match the player dimensions (32x32)
    pikachu_sprite._surf = pygame.transform.scale(pikachu_sprite._surf, (player.width, player.height))
    pikachu_sprite._update_pos()
    use_sprites = True
except:
    use_sprites = False  # Fall back to colored rectangles if sprite not found

def update():
    global game_state, current_level, camera_x, player, platforms, enemies, goal, use_sprites, space_was_pressed

    if game_state == GameState.PLAYING:
        # Handle input
        player.stop_horizontal()

        if keyboard.left or keyboard.a:
            player.move_left()
        elif keyboard.right or keyboard.d:
            player.move_right()

        # Detect spacebar press (not hold) for jumping
        space_is_pressed = keyboard.space
        if space_is_pressed and not space_was_pressed:
            player.jump()
        space_was_pressed = space_is_pressed

        # Update player
        old_y = player.y
        player.update()

        # Keep player on screen horizontally
        if player.x < 0:
            player.x = 0
        if player.x > 4900:  # Near end of level
            player.x = 4900

        # Platform collision detection
        player_rect = player.get_rect()
        player.on_ground = False

        for platform in platforms:
            platform_rect = platform.get_rect()

            # Check if player is standing on top of platform (even if just touching)
            if (player_rect.left < platform.right and player_rect.right > platform.left and
                abs(player.y + player.height - platform.top) <= 2 and player.vel_y >= 0):
                # Landing on top of platform
                player.y = platform.top - player.height
                player.vel_y = 0
                player.on_ground = True
                player.jumps_used = 0  # Reset jumps when landing
            elif player_rect.colliderect(platform_rect):
                # Other collisions (bottom and sides)
                if old_y >= platform.bottom and player.vel_y < 0:
                    # Hitting bottom of platform
                    player.y = platform.bottom
                    player.vel_y = 0
                else:
                    # Horizontal collision
                    if player.vel_x > 0:
                        player.x = platform.left - player.width
                    elif player.vel_x < 0:
                        player.x = platform.right

        # Update enemies
        for enemy in enemies:
            enemy.update(platforms)

        # Enemy collision detection
        for enemy in enemies:
            if not enemy.alive:
                continue

            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                # Check if player is stomping enemy (coming from above)
                if player.vel_y > 0 and player.y + player.height - 10 < enemy.y:
                    enemy.alive = False
                    player.vel_y = JUMP_SPEED / 2  # Small bounce
                else:
                    # Player hit from side - restart level
                    game_state = GameState.RESTARTING
                    return

        # Check goal collision
        if player_rect.colliderect(goal.get_rect()):
            game_state = GameState.LEVEL_COMPLETE

        # Update camera to follow player
        camera_x = player.x - WIDTH // 3
        camera_x = max(0, camera_x)

    elif game_state == GameState.LEVEL_COMPLETE:
        # Wait for space to continue to next level
        if keyboard.space:
            current_level += 1
            if current_level > 10:
                current_level = 1  # Loop back to level 1

            # Reset for next level
            player.x = 100
            player.y = HEIGHT - 100 - 32
            player.vel_x = 0
            player.vel_y = 0
            player.on_ground = True
            player.jumps_used = 0
            platforms, enemies, goal = generate_level(current_level)
            game_state = GameState.PLAYING

    elif game_state == GameState.RESTARTING:
        # Wait for space to restart
        if keyboard.space:
            # Reset level
            player.x = 100
            player.y = HEIGHT - 100 - 32
            player.vel_x = 0
            player.vel_y = 0
            player.on_ground = True
            player.jumps_used = 0
            platforms, enemies, goal = generate_level(current_level)
            game_state = GameState.PLAYING

def draw():
    screen.clear()
    screen.fill(SKY_BLUE)

    # Draw platforms (with camera offset)
    for platform in platforms:
        screen.draw.filled_rect(
            Rect(platform.x - camera_x, platform.y, platform.width, platform.height),
            BROWN
        )

    # Draw goal
    screen.draw.filled_rect(
        Rect(goal.x - camera_x, goal.y, goal.width, goal.height),
        GREEN
    )

    # Draw player (Pikachu)
    player_screen_x = player.x - camera_x
    if use_sprites:
        # Update sprite position and draw
        pikachu_sprite.topleft = (player_screen_x, player.y)
        pikachu_sprite.draw()
    else:
        # Fall back to colored rectangle
        screen.draw.filled_rect(
            Rect(player_screen_x, player.y, player.width, player.height),
            YELLOW
        )
        # Draw border around player to make it more visible
        screen.draw.rect(
            Rect(player_screen_x, player.y, player.width, player.height),
            (255, 0, 0)  # Red border
        )

    # Draw enemies (Eevee - pink squares for now)
    for enemy in enemies:
        if enemy.alive:
            screen.draw.filled_rect(
                Rect(enemy.x - camera_x, enemy.y, enemy.width, enemy.height),
                PINK
            )

    # Draw UI
    screen.draw.text(f"Level {current_level}/10", (10, 10), color="white", fontsize=30)
    screen.draw.text(f"Pikachu: ({int(player.x)}, {int(player.y)})", (10, 40), color="white", fontsize=20)

    if game_state == GameState.LEVEL_COMPLETE:
        screen.draw.text("LEVEL COMPLETE!", (WIDTH//2 - 150, HEIGHT//2 - 50),
                        color="white", fontsize=40)
        screen.draw.text("Press SPACE to continue", (WIDTH//2 - 130, HEIGHT//2 + 20),
                        color="white", fontsize=25)
    elif game_state == GameState.RESTARTING:
        screen.draw.text("HIT BY ENEMY!", (WIDTH//2 - 120, HEIGHT//2 - 50),
                        color="red", fontsize=40)
        screen.draw.text("Press SPACE to restart", (WIDTH//2 - 130, HEIGHT//2 + 20),
                        color="white", fontsize=25)
    else:
        # Show controls
        screen.draw.text("WASD/Arrows: Move | Space: Jump", (10, HEIGHT - 30),
                        color="white", fontsize=20)

pgzrun.go()
