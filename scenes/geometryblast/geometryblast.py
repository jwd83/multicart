# GeometryBlast - A Geometry Wars inspired twin-stick shooter
# WASD to move, mouse to aim and shoot

import pygame
import math
import random
from scene import Scene


# ============================================================================
# CONSTANTS
# ============================================================================

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# Player
PLAYER_SPEED = 4.5
PLAYER_SIZE = 12
PLAYER_FIRE_RATE = 5  # frames between shots

# Bullets
BULLET_SPEED = 12
BULLET_SIZE = 4
BULLET_LIFETIME = 60

# Enemies
ENEMY_SPAWN_INITIAL = 120  # frames between spawns
ENEMY_SPAWN_MIN = 20
SPAWN_RATE_DECREASE = 2  # decrease spawn interval every wave

# Particles
PARTICLE_GRAVITY = 0.1
TRAIL_LENGTH = 12
TRAIL_ALPHA_DECAY = 18

# Colors - Neon palette
COLOR_PLAYER = (0, 255, 255)  # Cyan
COLOR_PLAYER_GLOW = (0, 150, 200)
COLOR_BULLET = (255, 255, 100)
COLOR_BULLET_GLOW = (200, 200, 50)

# Enemy colors
ENEMY_COLORS = [
    (255, 50, 100),   # Pink
    (255, 150, 0),    # Orange
    (100, 255, 100),  # Green
    (255, 50, 255),   # Magenta
    (100, 150, 255),  # Blue
    (255, 255, 50),   # Yellow
]

# Background grid
GRID_COLOR = (20, 30, 50)
GRID_SPACING = 40


# ============================================================================
# PARTICLE SYSTEM
# ============================================================================

class Particle:
    """A single particle with physics and fading."""

    def __init__(self, x, y, vx, vy, color, size=3, lifetime=30, gravity=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.dead = False

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.gravity:
            self.vy += PARTICLE_GRAVITY
        self.vx *= 0.98  # friction
        self.vy *= 0.98
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.dead = True

    def draw(self, screen):
        t = self.lifetime / self.max_lifetime
        size = max(1, int(self.size * t))

        # Draw glow (dimmer version of color)
        if size > 2:
            glow_color = (int(self.color[0] * t * 0.3), int(self.color[1] * t * 0.3), int(self.color[2] * t * 0.3))
            pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), size * 2)

        # Draw core
        core_color = (int(self.color[0] * t), int(self.color[1] * t), int(self.color[2] * t))
        pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), size)


class TrailPoint:
    """A single point in a motion trail."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255


class ParticleSystem:
    """Manages all particles in the game."""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, speed=5, size=3, lifetime=30, spread=360, direction=0, gravity=True):
        """Emit particles in a burst."""
        for _ in range(count):
            angle = math.radians(direction + random.uniform(-spread/2, spread/2))
            spd = speed * random.uniform(0.5, 1.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            p = Particle(x, y, vx, vy, color,
                        size=size * random.uniform(0.5, 1.5),
                        lifetime=int(lifetime * random.uniform(0.7, 1.3)),
                        gravity=gravity)
            self.particles.append(p)

    def emit_explosion(self, x, y, color, intensity=1.0):
        """Create a dramatic explosion effect."""
        count = int(30 * intensity)
        self.emit(x, y, color, count=count, speed=8 * intensity, size=4, lifetime=40, gravity=True)
        # Add some sparkles
        self.emit(x, y, (255, 255, 255), count=count//3, speed=10 * intensity, size=2, lifetime=20, gravity=False)

    def emit_line(self, x1, y1, x2, y2, color, count=10, speed=2, size=2, lifetime=20):
        """Emit particles along a line."""
        for i in range(count):
            t = i / max(1, count - 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            angle = random.uniform(0, 360)
            vx = math.cos(math.radians(angle)) * speed * random.uniform(0.5, 1)
            vy = math.sin(math.radians(angle)) * speed * random.uniform(0.5, 1)
            p = Particle(x, y, vx, vy, color, size=size, lifetime=lifetime, gravity=False)
            self.particles.append(p)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


# ============================================================================
# GAME ENTITIES
# ============================================================================

class Player:
    """The player ship - a glowing geometric shape."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.size = PLAYER_SIZE
        self.fire_cooldown = 0
        self.trail = []
        self.invincible = 0
        self.dead = False

    def update(self, game, particles):
        # Movement with WASD
        dx, dy = 0, 0
        if game.pressed[pygame.K_w] or game.pressed[pygame.K_UP]:
            dy = -1
        if game.pressed[pygame.K_s] or game.pressed[pygame.K_DOWN]:
            dy = 1
        if game.pressed[pygame.K_a] or game.pressed[pygame.K_LEFT]:
            dx = -1
        if game.pressed[pygame.K_d] or game.pressed[pygame.K_RIGHT]:
            dx = 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        # Apply velocity with smoothing
        target_vx = dx * PLAYER_SPEED
        target_vy = dy * PLAYER_SPEED
        self.vx += (target_vx - self.vx) * 0.3
        self.vy += (target_vy - self.vy) * 0.3

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Keep in bounds with bounce
        margin = self.size
        if self.x < margin:
            self.x = margin
            self.vx *= -0.5
        if self.x > SCREEN_WIDTH - margin:
            self.x = SCREEN_WIDTH - margin
            self.vx *= -0.5
        if self.y < margin:
            self.y = margin
            self.vy *= -0.5
        if self.y > SCREEN_HEIGHT - margin:
            self.y = SCREEN_HEIGHT - margin
            self.vy *= -0.5

        # Update angle to face mouse
        mx, my = pygame.mouse.get_pos()
        self.angle = math.atan2(my - self.y, mx - self.x)

        # Fire cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

        # Invincibility
        if self.invincible > 0:
            self.invincible -= 1

        # Motion trail
        if abs(self.vx) > 0.5 or abs(self.vy) > 0.5:
            self.trail.append(TrailPoint(self.x, self.y, COLOR_PLAYER))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

        # Emit engine particles when moving
        if abs(self.vx) > 1 or abs(self.vy) > 1:
            engine_x = self.x - math.cos(self.angle) * self.size
            engine_y = self.y - math.sin(self.angle) * self.size
            particles.emit(engine_x, engine_y, COLOR_PLAYER_GLOW,
                          count=1, speed=2, size=2, lifetime=15, gravity=False)

    def shoot(self, particles):
        """Fire a bullet toward the mouse."""
        if self.fire_cooldown > 0:
            return None

        self.fire_cooldown = PLAYER_FIRE_RATE

        # Bullet spawns at nose of ship
        bx = self.x + math.cos(self.angle) * self.size
        by = self.y + math.sin(self.angle) * self.size

        # Muzzle flash
        particles.emit(bx, by, COLOR_BULLET, count=3, speed=3, size=2, lifetime=10, gravity=False)

        return Bullet(bx, by, self.angle)

    def draw(self, screen):
        # Skip drawing when blinking from invincibility
        if self.invincible > 0 and (self.invincible // 3) % 2 == 0:
            return

        # Draw trail
        for i, point in enumerate(self.trail):
            if len(self.trail) > 0:
                t = (i + 1) / len(self.trail)
                size = int(self.size * 0.4 * t)
                if size > 1:
                    color = (int(COLOR_PLAYER_GLOW[0] * t), int(COLOR_PLAYER_GLOW[1] * t), int(COLOR_PLAYER_GLOW[2] * t))
                    pygame.draw.circle(screen, color, (int(point.x), int(point.y)), size)

        # Draw outer glow circles
        pygame.draw.circle(screen, (0, 40, 50), (int(self.x), int(self.y)), int(self.size * 2))
        pygame.draw.circle(screen, (0, 80, 100), (int(self.x), int(self.y)), int(self.size * 1.5))

        # Draw the ship shape (diamond/arrow pointing toward mouse)
        points = []
        for i in range(4):
            a = self.angle + math.pi/2 * i
            r = self.size if i % 2 == 0 else self.size * 0.5
            if i == 0:  # Front point is longer
                r = self.size * 1.3
            px = self.x + math.cos(a) * r
            py = self.y + math.sin(a) * r
            points.append((px, py))

        # Draw shape
        pygame.draw.polygon(screen, COLOR_PLAYER, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)


class Bullet:
    """A player bullet."""

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.angle = angle
        self.lifetime = BULLET_LIFETIME
        self.dead = False
        self.trail = []

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Trail
        self.trail.append(TrailPoint(self.x, self.y, COLOR_BULLET))
        if len(self.trail) > 8:
            self.trail.pop(0)

        # Check bounds
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.dead = True
        if self.lifetime <= 0:
            self.dead = True

    def draw(self, screen):
        # Draw trail - bright yellow
        for i, point in enumerate(self.trail):
            if len(self.trail) > 0:
                t = (i + 1) / len(self.trail)
                pygame.draw.circle(screen, (255, 255, 0), (int(point.x), int(point.y)), 4)

        # Draw bullet - very bright and large
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), 10)  # Outer glow
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(self.y)), 6)  # Core
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 3)  # Center


class Enemy:
    """Base enemy class."""

    def __init__(self, x, y, enemy_type="diamond"):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.spin = random.uniform(-0.1, 0.1)
        self.size = 10
        self.enemy_type = enemy_type
        self.color = random.choice(ENEMY_COLORS)
        self.health = 1
        self.dead = False
        self.trail = []
        self.score_value = 100
        self.speed = 1.5

        # Type-specific properties
        if enemy_type == "diamond":
            self.size = 10
            self.speed = 1.8
            self.score_value = 100
        elif enemy_type == "square":
            self.size = 12
            self.speed = 1.2
            self.score_value = 150
            self.health = 2
        elif enemy_type == "triangle":
            self.size = 8
            self.speed = 2.5
            self.score_value = 75
        elif enemy_type == "hexagon":
            self.size = 15
            self.speed = 0.8
            self.score_value = 250
            self.health = 3
        elif enemy_type == "star":
            self.size = 12
            self.speed = 2.0
            self.score_value = 200
            self.spin = random.uniform(-0.2, 0.2)

    def update(self, player_x, player_y, particles):
        # Move toward player
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx += (dx / dist) * 0.1 * self.speed
            self.vy += (dy / dist) * 0.1 * self.speed

        # Limit speed
        speed = math.sqrt(self.vx*self.vx + self.vy*self.vy)
        if speed > self.speed * 2:
            self.vx = (self.vx / speed) * self.speed * 2
            self.vy = (self.vy / speed) * self.speed * 2

        self.x += self.vx
        self.y += self.vy
        self.angle += self.spin

        # Trail
        self.trail.append(TrailPoint(self.x, self.y, self.color))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

        # Occasional particle emission
        if random.random() < 0.1:
            particles.emit(self.x, self.y, self.color, count=1, speed=1, size=2, lifetime=20, gravity=False)

    def hit(self, particles):
        """Take a hit. Returns True if dead."""
        self.health -= 1
        if self.health <= 0:
            self.dead = True
            particles.emit_explosion(self.x, self.y, self.color, intensity=1.0)
            return True
        else:
            # Hit flash
            particles.emit(self.x, self.y, (255, 255, 255), count=5, speed=4, size=2, lifetime=15, gravity=False)
            return False

    def draw(self, screen):
        # Draw trail
        for i, point in enumerate(self.trail):
            if len(self.trail) > 0:
                t = (i + 1) / len(self.trail)
                size = int(self.size * 0.3 * t)
                if size > 1:
                    color = (int(self.color[0] * t * 0.5), int(self.color[1] * t * 0.5), int(self.color[2] * t * 0.5))
                    pygame.draw.circle(screen, color, (int(point.x), int(point.y)), size)

        # Draw glow
        glow_color = (self.color[0] // 4, self.color[1] // 4, self.color[2] // 4)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), int(self.size * 1.8))
        glow_color2 = (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2)
        pygame.draw.circle(screen, glow_color2, (int(self.x), int(self.y)), int(self.size * 1.3))

        # Draw shape based on type
        points = self._get_shape_points(self.x, self.y)
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)

    def _get_shape_points(self, cx, cy):
        """Get polygon points for this enemy type."""
        points = []

        if self.enemy_type == "diamond":
            for i in range(4):
                a = self.angle + math.pi/2 * i
                px = cx + math.cos(a) * self.size
                py = cy + math.sin(a) * self.size
                points.append((int(px), int(py)))

        elif self.enemy_type == "square":
            for i in range(4):
                a = self.angle + math.pi/2 * i + math.pi/4
                px = cx + math.cos(a) * self.size * 1.2
                py = cy + math.sin(a) * self.size * 1.2
                points.append((int(px), int(py)))

        elif self.enemy_type == "triangle":
            for i in range(3):
                a = self.angle + math.pi*2/3 * i - math.pi/2
                px = cx + math.cos(a) * self.size
                py = cy + math.sin(a) * self.size
                points.append((int(px), int(py)))

        elif self.enemy_type == "hexagon":
            for i in range(6):
                a = self.angle + math.pi/3 * i
                px = cx + math.cos(a) * self.size
                py = cy + math.sin(a) * self.size
                points.append((int(px), int(py)))

        elif self.enemy_type == "star":
            for i in range(10):
                a = self.angle + math.pi/5 * i
                r = self.size if i % 2 == 0 else self.size * 0.5
                px = cx + math.cos(a) * r
                py = cy + math.sin(a) * r
                points.append((int(px), int(py)))

        return points


# ============================================================================
# POWERUPS
# ============================================================================

class Powerup:
    """Collectible powerup that spawns from killed enemies."""

    TYPES = ["rapid", "spread", "shield", "bomb", "multiplier"]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.powerup_type = random.choice(self.TYPES)
        self.size = 8
        self.lifetime = 600  # 10 seconds
        self.pulse = 0
        self.dead = False

        # Type-specific colors
        self.colors = {
            "rapid": (255, 255, 0),     # Yellow - faster shooting
            "spread": (255, 100, 255),   # Pink - triple shot
            "shield": (0, 255, 255),     # Cyan - temporary invincibility
            "bomb": (255, 50, 50),       # Red - screen clear
            "multiplier": (100, 255, 100), # Green - 2x multiplier
        }
        self.color = self.colors[self.powerup_type]

    def update(self):
        self.pulse += 0.2
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.dead = True

    def draw(self, screen):
        # Pulsing effect
        pulse_size = self.size + math.sin(self.pulse) * 3
        brightness = 1.0 if self.lifetime > 60 else (self.lifetime / 60)

        # Outer glow
        glow_color = (int(self.color[0] * 0.3 * brightness), int(self.color[1] * 0.3 * brightness), int(self.color[2] * 0.3 * brightness))
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), int(pulse_size * 2))

        # Inner glow
        glow_color2 = (int(self.color[0] * 0.6 * brightness), int(self.color[1] * 0.6 * brightness), int(self.color[2] * 0.6 * brightness))
        pygame.draw.circle(screen, glow_color2, (int(self.x), int(self.y)), int(pulse_size * 1.3))

        # Core color
        core_color = (int(self.color[0] * brightness), int(self.color[1] * brightness), int(self.color[2] * brightness))
        cx, cy = int(self.x), int(self.y)

        # Core shape based on type
        if self.powerup_type == "rapid":
            # Lightning bolt
            points = [(cx-4, cy-6), (cx+2, cy-2), (cx-1, cy), (cx+4, cy+6), (cx-2, cy+2), (cx+1, cy)]
            pygame.draw.polygon(screen, core_color, points)
        elif self.powerup_type == "spread":
            # Three dots
            for angle in [0, 120, 240]:
                px = cx + math.cos(math.radians(angle - 90)) * 4
                py = cy + math.sin(math.radians(angle - 90)) * 4
                pygame.draw.circle(screen, core_color, (int(px), int(py)), 3)
        elif self.powerup_type == "shield":
            # Circle with inner circle
            pygame.draw.circle(screen, core_color, (cx, cy), int(pulse_size), 2)
            pygame.draw.circle(screen, core_color, (cx, cy), int(pulse_size * 0.5))
        elif self.powerup_type == "bomb":
            # Explosion shape
            for i in range(8):
                angle = math.radians(i * 45 + self.pulse * 30)
                r = pulse_size * (0.8 if i % 2 == 0 else 0.5)
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                pygame.draw.circle(screen, core_color, (int(px), int(py)), 2)
        else:  # multiplier
            # Star shape
            points = []
            for i in range(8):
                angle = math.radians(i * 45 - 90)
                r = pulse_size if i % 2 == 0 else pulse_size * 0.4
                points.append((int(cx + math.cos(angle) * r), int(cy + math.sin(angle) * r)))
            pygame.draw.polygon(screen, core_color, points)


# ============================================================================
# MAIN GAME SCENE
# ============================================================================

class GeometryBlast(Scene):
    """GeometryBlast - A Geometry Wars inspired twin-stick shooter."""

    def __init__(self, game):
        super().__init__(game)

        # Hide system mouse
        self.mouse_hide = True

        # Game state
        self.state = "playing"
        self.score = 0
        self.multiplier = 1
        self.lives = 3
        self.wave = 1

        # Spawn control
        self.spawn_timer = 60
        self.spawn_interval = ENEMY_SPAWN_INITIAL
        self.enemies_per_wave = 5
        self.enemies_spawned_this_wave = 0
        self.enemies_to_spawn = 5

        # Game objects
        self.player = Player(CENTER_X, CENTER_Y)
        self.bullets = []
        self.enemies = []
        self.particles = ParticleSystem()
        self.powerups = []

        # Powerup effects
        self.rapid_fire = 0       # frames remaining
        self.spread_shot = 0      # frames remaining
        self.shield = 0           # frames remaining

        # UI
        self.standard_font_size = 20
        self.standard_stroke = True
        self.standard_stroke_color = (0, 0, 0)
        self.standard_stroke_thickness = 2

        # Visual effects
        self.border_pulse = 0
        self.frame_count = 0
        self.wave_announcement = 0

        # Screen shake
        self.screen_shake = 0
        self.shake_x = 0
        self.shake_y = 0

        # Create background surface
        self.bg_surface = self._create_background()

    def _create_background(self):
        """Create the background grid."""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surf.fill((5, 8, 15))

        # Draw grid lines
        for x in range(0, SCREEN_WIDTH + GRID_SPACING, GRID_SPACING):
            pygame.draw.line(surf, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT + GRID_SPACING, GRID_SPACING):
            pygame.draw.line(surf, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)

        # Add some subtle gradient/vignette
        for i in range(50):
            alpha = 3
            rect = pygame.Rect(i, i, SCREEN_WIDTH - i*2, SCREEN_HEIGHT - i*2)
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(surf, (0, 0, 0, alpha), rect, 1)

        return surf

    def spawn_enemy(self):
        """Spawn a new enemy at the edge of the screen."""
        # Choose spawn edge
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            x = random.randint(0, SCREEN_WIDTH)
            y = -20
        elif edge == 1:  # Right
            x = SCREEN_WIDTH + 20
            y = random.randint(0, SCREEN_HEIGHT)
        elif edge == 2:  # Bottom
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 20
        else:  # Left
            x = -20
            y = random.randint(0, SCREEN_HEIGHT)

        # Choose enemy type based on wave
        types = ["diamond", "triangle"]
        if self.wave >= 2:
            types.append("square")
        if self.wave >= 3:
            types.append("star")
        if self.wave >= 5:
            types.append("hexagon")

        enemy_type = random.choice(types)
        enemy = Enemy(x, y, enemy_type)
        self.enemies.append(enemy)

        # Spawn particles
        self.particles.emit(x, y, enemy.color, count=10, speed=5, lifetime=30, gravity=False)

    def start_new_wave(self):
        """Start a new wave of enemies."""
        self.wave += 1
        self.enemies_to_spawn = 5 + self.wave * 2
        self.enemies_spawned_this_wave = 0
        self.spawn_interval = max(ENEMY_SPAWN_MIN, ENEMY_SPAWN_INITIAL - self.wave * SPAWN_RATE_DECREASE)
        self.wave_announcement = 90  # Show wave text for 90 frames
        self.play_sound("level-up-bonus-sequence-2-186891")

        # Wave announcement particles - radial burst
        for i in range(60):
            angle = (i / 60) * math.pi * 2
            self.particles.emit(
                CENTER_X + math.cos(angle) * 50,
                CENTER_Y + math.sin(angle) * 50,
                (100, 200, 255),
                count=1, speed=8, size=4, lifetime=60, direction=math.degrees(angle), spread=30, gravity=False
            )

    def respawn_player(self):
        """Respawn the player after death."""
        self.player = Player(CENTER_X, CENTER_Y)
        self.player.invincible = 120  # 2 seconds of invincibility
        self.multiplier = 1

        # Clear nearby enemies
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - CENTER_X)**2 + (enemy.y - CENTER_Y)**2)
            if dist < 100:
                enemy.dead = True
                self.particles.emit_explosion(enemy.x, enemy.y, enemy.color)

    def game_over(self):
        """Handle game over."""
        self.state = "gameover"
        self.play_sound("game-over-arcade-6435")
        # Big explosion
        for _ in range(5):
            self.particles.emit_explosion(self.player.x, self.player.y, COLOR_PLAYER, intensity=2.0)

    def restart_game(self):
        """Restart the game."""
        self.state = "playing"
        self.score = 0
        self.multiplier = 1
        self.lives = 3
        self.wave = 1
        self.spawn_interval = ENEMY_SPAWN_INITIAL
        self.enemies_to_spawn = 5
        self.enemies_spawned_this_wave = 0
        self.player = Player(CENTER_X, CENTER_Y)
        self.bullets = []
        self.enemies = []
        self.particles = ParticleSystem()
        self.powerups = []
        self.rapid_fire = 0
        self.spread_shot = 0
        self.shield = 0
        self.wave_announcement = 0

    def update(self):
        """Update game state."""
        self.frame_count += 1
        self.border_pulse += 0.05

        # Wave announcement timer
        if self.wave_announcement > 0:
            self.wave_announcement -= 1

        # Handle escape
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            return

        # Handle game over state
        if self.state == "gameover":
            self.particles.update()
            if 1 in self.game.just_mouse_down or pygame.K_SPACE in self.game.just_pressed:
                self.restart_game()
            return

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.shake_x = random.randint(-self.screen_shake, self.screen_shake)
            self.shake_y = random.randint(-self.screen_shake, self.screen_shake)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Update powerup timers
        if self.rapid_fire > 0:
            self.rapid_fire -= 1
        if self.spread_shot > 0:
            self.spread_shot -= 1
        if self.shield > 0:
            self.shield -= 1
            self.player.invincible = max(self.player.invincible, 1)

        # Update player
        self.player.update(self.game, self.particles)

        # Shooting - check for rapid fire and spread shot
        fire_rate = PLAYER_FIRE_RATE // 2 if self.rapid_fire > 0 else PLAYER_FIRE_RATE
        self.player.fire_cooldown = min(self.player.fire_cooldown, fire_rate)

        # Check for held mouse button or space for continuous fire
        mouse_held = pygame.mouse.get_pressed()[0]
        space_held = self.game.pressed[pygame.K_SPACE]

        if mouse_held or space_held:
            if self.player.fire_cooldown <= 0:
                self.player.fire_cooldown = fire_rate
                self.play_sound("shoot")

                # Spawn position at nose of ship
                bx = self.player.x + math.cos(self.player.angle) * self.player.size
                by = self.player.y + math.sin(self.player.angle) * self.player.size

                # Calculate bullet(s)
                if self.spread_shot > 0:
                    # Triple shot
                    for angle_offset in [-0.2, 0, 0.2]:
                        bullet = Bullet(bx, by, self.player.angle + angle_offset)
                        self.bullets.append(bullet)
                    self.particles.emit(bx, by, COLOR_BULLET, count=5, speed=3, size=2, lifetime=10, gravity=False)
                else:
                    # Single shot
                    bullet = Bullet(bx, by, self.player.angle)
                    self.bullets.append(bullet)
                    # Muzzle flash
                    self.particles.emit(bx, by, COLOR_BULLET, count=3, speed=3, size=2, lifetime=10, gravity=False)

        # Update bullets
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if not b.dead]

        # Update powerups
        for powerup in self.powerups:
            powerup.update()
            # Check pickup
            dist = math.sqrt((self.player.x - powerup.x)**2 + (self.player.y - powerup.y)**2)
            if dist < self.player.size + powerup.size:
                self._collect_powerup(powerup)
        self.powerups = [p for p in self.powerups if not p.dead]

        # Spawn enemies
        self.spawn_timer -= 1
        if self.spawn_timer <= 0 and self.enemies_spawned_this_wave < self.enemies_to_spawn:
            self.spawn_enemy()
            self.enemies_spawned_this_wave += 1
            self.spawn_timer = self.spawn_interval

        # Check for wave completion
        if self.enemies_spawned_this_wave >= self.enemies_to_spawn and len(self.enemies) == 0:
            self.start_new_wave()

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y, self.particles)

        # Bullet-enemy collisions
        for bullet in self.bullets:
            if bullet.dead:
                continue
            for enemy in self.enemies:
                if enemy.dead:
                    continue
                dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                if dist < enemy.size + BULLET_SIZE:
                    bullet.dead = True
                    if enemy.hit(self.particles):
                        self.score += enemy.score_value * self.multiplier
                        self.multiplier = min(10, self.multiplier + 0.1)
                        self.screen_shake = 5
                        self.play_sound("hit")
                        # Chance to spawn powerup
                        if random.random() < 0.15:
                            self.powerups.append(Powerup(enemy.x, enemy.y))
                    break

        # Player-enemy collisions
        if self.player.invincible <= 0 and self.shield <= 0:
            for enemy in self.enemies:
                if enemy.dead:
                    continue
                dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                if dist < enemy.size + self.player.size:
                    # Player hit!
                    self.lives -= 1
                    self.screen_shake = 15
                    self.particles.emit_explosion(self.player.x, self.player.y, COLOR_PLAYER, intensity=2.0)
                    self.play_sound("death1")

                    if self.lives <= 0:
                        self.game_over()
                    else:
                        self.respawn_player()
                    break

        # Clean up dead enemies
        self.enemies = [e for e in self.enemies if not e.dead]

        # Update particles
        self.particles.update()

    def _collect_powerup(self, powerup):
        """Apply powerup effect."""
        powerup.dead = True
        self.screen_shake = 3
        self.play_sound("cute-level-up-1-189852")

        # Visual feedback
        self.particles.emit(powerup.x, powerup.y, powerup.color, count=20, speed=6, size=3, lifetime=30, gravity=False)

        if powerup.powerup_type == "rapid":
            self.rapid_fire = 300  # 5 seconds
        elif powerup.powerup_type == "spread":
            self.spread_shot = 300
        elif powerup.powerup_type == "shield":
            self.shield = 300
            self.player.invincible = 300
        elif powerup.powerup_type == "bomb":
            # Clear all enemies
            for enemy in self.enemies:
                self.score += enemy.score_value * self.multiplier
                self.particles.emit_explosion(enemy.x, enemy.y, enemy.color, intensity=0.5)
                enemy.dead = True
            self.screen_shake = 20
        elif powerup.powerup_type == "multiplier":
            self.multiplier = min(10, self.multiplier * 2)

    def draw(self):
        """Draw the game."""
        # Apply screen shake offset
        offset_x = self.shake_x
        offset_y = self.shake_y

        # Draw background
        self.screen.blit(self.bg_surface, (offset_x, offset_y))

        # Draw pulsing border
        self._draw_border()

        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw particles (behind entities)
        self.particles.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw player
        if self.state == "playing":
            self.player.draw(self.screen)
            # Draw shield effect
            if self.shield > 0:
                self._draw_shield(self.screen)

        # Wave announcement
        if self.wave_announcement > 0:
            self._draw_wave_announcement()

        # Draw UI
        self._draw_ui()

        # Draw crosshair
        self._draw_crosshair()

        # Draw game over overlay
        if self.state == "gameover":
            self._draw_game_over()

    def _draw_border(self):
        """Draw animated neon border."""
        # Calculate border color based on game state
        if len(self.enemies) > 10:
            # Danger - red pulse
            intensity = int(100 + math.sin(self.border_pulse * 4) * 50)
            color = (intensity, 20, 20)
        elif self.shield > 0:
            # Shield active - cyan pulse
            intensity = int(100 + math.sin(self.border_pulse * 3) * 55)
            color = (20, intensity, intensity)
        else:
            # Normal - subtle blue pulse
            intensity = int(30 + math.sin(self.border_pulse) * 20)
            color = (intensity // 2, intensity // 2, intensity)

        # Draw border lines
        thickness = 3
        pygame.draw.rect(self.screen, color, (0, 0, SCREEN_WIDTH, thickness))
        pygame.draw.rect(self.screen, color, (0, SCREEN_HEIGHT - thickness, SCREEN_WIDTH, thickness))
        pygame.draw.rect(self.screen, color, (0, 0, thickness, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, color, (SCREEN_WIDTH - thickness, 0, thickness, SCREEN_HEIGHT))

        # Corner accents
        corner_size = 20
        pygame.draw.line(self.screen, color, (0, corner_size), (corner_size, 0), 2)
        pygame.draw.line(self.screen, color, (SCREEN_WIDTH, corner_size), (SCREEN_WIDTH - corner_size, 0), 2)
        pygame.draw.line(self.screen, color, (0, SCREEN_HEIGHT - corner_size), (corner_size, SCREEN_HEIGHT), 2)
        pygame.draw.line(self.screen, color, (SCREEN_WIDTH, SCREEN_HEIGHT - corner_size), (SCREEN_WIDTH - corner_size, SCREEN_HEIGHT), 2)

    def _draw_shield(self, surface):
        """Draw shield effect around player."""
        pulse = math.sin(self.frame_count * 0.2) * 5
        radius = int(self.player.size * 2 + pulse)
        brightness = 1.0 if self.shield > 60 else (self.shield / 60)

        cx, cy = int(self.player.x), int(self.player.y)

        # Draw shield rings
        color1 = (0, int(100 * brightness), int(100 * brightness))
        color2 = (0, int(180 * brightness), int(180 * brightness))
        color3 = (int(50 * brightness), int(200 * brightness), int(200 * brightness))

        pygame.draw.circle(surface, color1, (cx, cy), radius + 5, 2)
        pygame.draw.circle(surface, color2, (cx, cy), radius, 2)
        pygame.draw.circle(surface, color3, (cx, cy), radius - 4, 1)

        # Rotating dots
        for i in range(6):
            angle = self.frame_count * 0.1 + i * math.pi / 3
            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius
            pygame.draw.circle(surface, (int(255 * brightness), int(255 * brightness), int(255 * brightness)), (int(px), int(py)), 3)

    def _draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.make_text(f"SCORE: {int(self.score)}", (255, 255, 255), 24)
        self.screen.blit(score_text, (10, 10))

        # Multiplier
        mult_color = (255, 255, 100) if self.multiplier > 1 else (150, 150, 150)
        mult_text = self.make_text(f"x{self.multiplier:.1f}", mult_color, 20)
        self.screen.blit(mult_text, (10, 40))

        # Wave
        wave_text = self.make_text(f"WAVE {self.wave}", (100, 200, 255), 20)
        self.screen.blit(wave_text, (SCREEN_WIDTH - wave_text.get_width() - 10, 10))

        # Debug: bullet count
        bullet_text = self.make_text(f"BULLETS: {len(self.bullets)}", (255, 255, 0), 14)
        self.screen.blit(bullet_text, (SCREEN_WIDTH - bullet_text.get_width() - 10, 35))

        # Lives
        for i in range(self.lives):
            x = SCREEN_WIDTH - 30 - i * 25
            y = 45
            # Draw mini player shape
            pygame.draw.polygon(self.screen, COLOR_PLAYER, [
                (x, y - 8),
                (x + 6, y),
                (x, y + 8),
                (x - 6, y)
            ])

        # Active powerups indicator
        powerup_y = SCREEN_HEIGHT - 25
        powerup_x = 10
        if self.rapid_fire > 0:
            pygame.draw.rect(self.screen, (255, 255, 0), (powerup_x, powerup_y, 30, 15))
            pct = self.rapid_fire / 300
            pygame.draw.rect(self.screen, (200, 200, 0), (powerup_x, powerup_y, int(30 * pct), 15))
            rapid_txt = self.make_text("RAPID", (0, 0, 0), 10)
            self.screen.blit(rapid_txt, (powerup_x + 2, powerup_y + 2))
            powerup_x += 35

        if self.spread_shot > 0:
            pygame.draw.rect(self.screen, (255, 100, 255), (powerup_x, powerup_y, 40, 15))
            pct = self.spread_shot / 300
            pygame.draw.rect(self.screen, (200, 50, 200), (powerup_x, powerup_y, int(40 * pct), 15))
            spread_txt = self.make_text("SPREAD", (0, 0, 0), 10)
            self.screen.blit(spread_txt, (powerup_x + 2, powerup_y + 2))
            powerup_x += 45

        if self.shield > 0:
            pygame.draw.rect(self.screen, (0, 255, 255), (powerup_x, powerup_y, 40, 15))
            pct = self.shield / 300
            pygame.draw.rect(self.screen, (0, 200, 200), (powerup_x, powerup_y, int(40 * pct), 15))
            shield_txt = self.make_text("SHIELD", (0, 0, 0), 10)
            self.screen.blit(shield_txt, (powerup_x + 2, powerup_y + 2))

    def _draw_wave_announcement(self):
        """Draw wave start announcement."""
        # Calculate animation progress (0 to 1)
        progress = 1 - (self.wave_announcement / 90)

        # Scale and alpha animation
        if progress < 0.3:
            scale = progress / 0.3
            alpha = int(255 * (progress / 0.3))
        elif progress > 0.7:
            scale = 1.0
            alpha = int(255 * (1 - (progress - 0.7) / 0.3))
        else:
            scale = 1.0
            alpha = 255

        # Create wave text
        wave_text = f"WAVE {self.wave}"
        font_size = int(60 * scale)
        if font_size > 0:
            text_surf = self.make_text(wave_text, (100, 200, 255), font_size)

            # Apply alpha
            text_surf.set_alpha(alpha)

            # Center on screen
            text_rect = text_surf.get_rect(center=(CENTER_X, CENTER_Y))
            self.screen.blit(text_surf, text_rect)

    def _draw_crosshair(self):
        """Draw the crosshair cursor."""
        mx, my = pygame.mouse.get_pos()

        # Crosshair
        size = 10
        gap = 4
        color = (255, 255, 255)

        # Lines
        pygame.draw.line(self.screen, color, (mx - size, my), (mx - gap, my), 2)
        pygame.draw.line(self.screen, color, (mx + gap, my), (mx + size, my), 2)
        pygame.draw.line(self.screen, color, (mx, my - size), (mx, my - gap), 2)
        pygame.draw.line(self.screen, color, (mx, my + gap), (mx, my + size), 2)

        # Center dot
        pygame.draw.circle(self.screen, color, (mx, my), 2)

    def _draw_game_over(self):
        """Draw game over screen."""
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        go_text = self.make_text("GAME OVER", (255, 50, 100), 60)
        go_rect = go_text.get_rect(center=(CENTER_X, CENTER_Y - 40))
        self.screen.blit(go_text, go_rect)

        # Final score
        score_text = self.make_text(f"FINAL SCORE: {int(self.score)}", (255, 255, 255), 30)
        score_rect = score_text.get_rect(center=(CENTER_X, CENTER_Y + 20))
        self.screen.blit(score_text, score_rect)

        # Wave reached
        wave_text = self.make_text(f"WAVE {self.wave}", (100, 200, 255), 24)
        wave_rect = wave_text.get_rect(center=(CENTER_X, CENTER_Y + 55))
        self.screen.blit(wave_text, wave_rect)

        # Restart prompt
        restart_text = self.make_text("CLICK or SPACE to restart", (150, 150, 150), 18)
        restart_rect = restart_text.get_rect(center=(CENTER_X, CENTER_Y + 100))
        self.screen.blit(restart_text, restart_rect)
