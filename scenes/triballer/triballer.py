# Tri-Baller - Bubble shooter game

import pygame
import random
from scene import Scene
from .scripts.constants import (
    BUBBLE_RADIUS, BUBBLE_DIAMETER, GRID_COLS, GRID_MAX_ROWS,
    PLAYFIELD_LEFT, PLAYFIELD_WIDTH, PLAYFIELD_TOP,
    SHOOTER_X, SHOOTER_Y, DANGER_ROW,
    STATE_AIMING, STATE_SHOOTING, STATE_MATCHING, STATE_FALLING,
    STATE_GAME_OVER, STATE_WIN,
    MATCH_FLASH_FRAMES, FALL_SHAKE_FRAMES, SHOTS_BEFORE_DROP,
    get_color
)
from .scripts.board import HexBoard
from .scripts.bubble import FlyingBubble, BubbleParticle
from .scripts.shooter import Shooter


class TriBaller(Scene):
    """Tri-Baller bubble shooter game scene."""

    def __init__(self, game):
        super().__init__(game)

        # Game components
        self.board = HexBoard()
        self.shooter = Shooter(self.board)
        self.flying_bubble = None
        self.particle_group = pygame.sprite.Group()

        # Game state
        self.state = STATE_AIMING
        self.score = 0
        self.shots_without_match = 0
        self.level = 1

        # Animation state
        self.anim_timer = 0
        self.matched_bubbles = []
        self.falling_bubbles = []

        # UI
        self.standard_font_size = 20
        self.standard_stroke = True
        self.standard_stroke_color = (0, 0, 0)
        self.standard_stroke_thickness = 1

        # Load background image
        self.bg_image = pygame.image.load("assets/triballer/triballerbg.png").convert()

        # Initialize level
        self.start_new_game()

    def start_new_game(self):
        """Start a new game."""
        self.board.generate_level(num_rows=6, num_colors=5 + min(2, self.level - 1))
        self.shooter = Shooter(self.board)
        self.flying_bubble = None
        self.state = STATE_AIMING
        self.score = 0
        self.shots_without_match = 0
        self.matched_bubbles = []
        self.falling_bubbles = []
        self.particle_group.empty()

    def update(self):
        """Update game state."""
        # Handle escape to return to menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            return

        # Handle game over / win states
        if self.state in (STATE_GAME_OVER, STATE_WIN):
            if self.game.just_mouse_down or pygame.K_SPACE in self.game.just_pressed:
                if self.state == STATE_WIN:
                    self.level += 1
                else:
                    self.level = 1
                self.start_new_game()
            return

        # Update particles
        self.particle_group.update()

        # State machine
        if self.state == STATE_AIMING:
            self._update_aiming()
        elif self.state == STATE_SHOOTING:
            self._update_shooting()
        elif self.state == STATE_MATCHING:
            self._update_matching()
        elif self.state == STATE_FALLING:
            self._update_falling()

    def _update_aiming(self):
        """Handle aiming state - player controls aim."""
        # Update aim based on mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.shooter.aim_at(mouse_x, mouse_y)

        # Swap bubbles with right click or S key
        if 3 in self.game.just_mouse_down or pygame.K_s in self.game.just_pressed:
            self.shooter.swap_bubbles()
            self.play_sound("jsfxr-drop2")

        # Shoot on left click or space
        if 1 in self.game.just_mouse_down or pygame.K_SPACE in self.game.just_pressed:
            x, y, angle, color = self.shooter.shoot()
            self.flying_bubble = FlyingBubble(x, y, angle, color)
            self.state = STATE_SHOOTING
            self.play_sound("jsfxr-drop2")

    def _update_shooting(self):
        """Handle shooting state - bubble flying."""
        if not self.flying_bubble:
            self.state = STATE_AIMING
            return

        self.flying_bubble.update()

        # Check collision with ceiling
        if self.flying_bubble.hit_ceiling():
            self._snap_bubble()
            return

        # Check collision with other bubbles
        bubble_x = self.flying_bubble.x
        bubble_y = self.flying_bubble.y

        for row in range(GRID_MAX_ROWS):
            max_col = GRID_COLS - 1 if row % 2 == 0 else GRID_COLS - 2
            for col in range(max_col + 1):
                if self.board.get_bubble(row, col) > 0:
                    bx, by = self.board.grid_to_screen(row, col)
                    dist = ((bubble_x - bx) ** 2 + (bubble_y - by) ** 2) ** 0.5
                    if dist < BUBBLE_DIAMETER - 2:
                        self._snap_bubble()
                        return

    def _snap_bubble(self):
        """Snap the flying bubble to the grid and check for matches."""
        if not self.flying_bubble:
            return

        # Find snap position
        row, col = self.board.find_snap_position(
            self.flying_bubble.x, self.flying_bubble.y
        )

        # Place bubble on board
        self.board.set_bubble(row, col, self.flying_bubble.color)
        self.flying_bubble = None

        # Check for matches (3+ connected same color)
        connected = self.board.find_connected_same_color(row, col)

        if len(connected) >= 3:
            self.matched_bubbles = connected
            self.state = STATE_MATCHING
            self.anim_timer = MATCH_FLASH_FRAMES
            self.shots_without_match = 0
        else:
            # No match, check if we need to push ceiling down
            self.shots_without_match += 1
            if self.shots_without_match >= SHOTS_BEFORE_DROP:
                self.shots_without_match = 0
                self.board.add_row_at_top()

            # Check for game over
            if self.board.check_game_over():
                self.state = STATE_GAME_OVER
            else:
                self.shooter.refresh_colors()
                self.state = STATE_AIMING

    def _update_matching(self):
        """Handle matching animation state."""
        self.anim_timer -= 1

        if self.anim_timer <= 0:
            # Create pop particles and remove matched bubbles
            for row, col in self.matched_bubbles:
                x, y = self.board.grid_to_screen(row, col)
                color = self.board.get_bubble(row, col)
                for _ in range(5):
                    self.particle_group.add(BubbleParticle(x, y, color, "pop"))

            # Add score
            self.score += len(self.matched_bubbles) * 10

            # Remove matched bubbles
            self.board.remove_bubbles(self.matched_bubbles)
            self.matched_bubbles = []

            # Play pop sound
            self.play_sound("level-up-bonus-sequence-1-186890")

            # Check for floating bubbles
            self.falling_bubbles = self.board.find_floating_bubbles()

            if self.falling_bubbles:
                self.state = STATE_FALLING
                self.anim_timer = FALL_SHAKE_FRAMES
            else:
                self._check_win_or_continue()

    def _update_falling(self):
        """Handle falling animation state."""
        self.anim_timer -= 1

        if self.anim_timer <= 0:
            # Create fall particles and remove floating bubbles
            for row, col in self.falling_bubbles:
                x, y = self.board.grid_to_screen(row, col)
                color = self.board.get_bubble(row, col)
                for _ in range(3):
                    self.particle_group.add(BubbleParticle(x, y, color, "fall"))

            # Bonus score for falling bubbles
            self.score += len(self.falling_bubbles) * 20

            # Remove floating bubbles
            self.board.remove_bubbles(self.falling_bubbles)
            self.falling_bubbles = []

            # Play fall sound
            self.play_sound("level-up-bonus-sequence-2-186891")

            self._check_win_or_continue()

    def _check_win_or_continue(self):
        """Check for win condition or return to aiming."""
        if self.board.is_empty():
            self.state = STATE_WIN
        elif self.board.check_game_over():
            self.state = STATE_GAME_OVER
        else:
            self.shooter.refresh_colors()
            self.state = STATE_AIMING

    def draw(self):
        """Draw the game."""
        # Draw background
        self.screen.blit(self.bg_image, (0, 0))

        # Draw danger line
        danger_y = PLAYFIELD_TOP + DANGER_ROW * BUBBLE_DIAMETER
        pygame.draw.line(
            self.screen,
            (150, 50, 50),
            (PLAYFIELD_LEFT, danger_y),
            (PLAYFIELD_LEFT + PLAYFIELD_WIDTH, danger_y),
            2
        )

        # Draw grid bubbles
        self._draw_bubbles()

        # Draw shooter
        self.shooter.draw(self.screen)

        # Draw flying bubble
        if self.flying_bubble:
            self.flying_bubble.draw(self.screen)

        # Draw particles
        self.particle_group.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw game over / win overlay
        if self.state == STATE_GAME_OVER:
            self._draw_overlay("GAME OVER", "Click to restart")
        elif self.state == STATE_WIN:
            self._draw_overlay(f"LEVEL {self.level} CLEAR!", "Click for next level")

    def _draw_bubbles(self):
        """Draw all bubbles on the board."""
        for row in range(GRID_MAX_ROWS):
            max_col = GRID_COLS - 1 if row % 2 == 0 else GRID_COLS - 2
            for col in range(max_col + 1):
                color_idx = self.board.get_bubble(row, col)
                if color_idx > 0:
                    x, y = self.board.grid_to_screen(row, col)
                    color = get_color(color_idx)

                    # Apply animation effects
                    draw_x, draw_y = x, y

                    # Flash effect for matching bubbles
                    if (row, col) in self.matched_bubbles:
                        if self.anim_timer % 4 < 2:
                            color = (255, 255, 255)

                    # Shake effect for falling bubbles
                    if (row, col) in self.falling_bubbles:
                        draw_x += random.randint(-2, 2)
                        draw_y += random.randint(-2, 2)

                    # Draw bubble
                    pygame.draw.circle(self.screen, color, (int(draw_x), int(draw_y)), BUBBLE_RADIUS)

                    # Draw highlight
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (int(draw_x - BUBBLE_RADIUS // 3), int(draw_y - BUBBLE_RADIUS // 3)),
                        BUBBLE_RADIUS // 3
                    )

                    # Draw outline
                    pygame.draw.circle(
                        self.screen,
                        (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40)),
                        (int(draw_x), int(draw_y)),
                        BUBBLE_RADIUS,
                        1
                    )

    def _draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.standard_text(f"SCORE: {self.score}")
        self.screen.blit(score_text, (10, 10))

        # Level
        level_text = self.standard_text(f"LEVEL: {self.level}")
        self.screen.blit(level_text, (10, 35))

        # Shots until drop
        remaining = SHOTS_BEFORE_DROP - self.shots_without_match
        drop_text = self.make_text(
            f"DROP IN: {remaining}",
            (200, 150, 150) if remaining <= 2 else (150, 150, 150),
            16
        )
        self.screen.blit(drop_text, (PLAYFIELD_LEFT + PLAYFIELD_WIDTH + 15, 30))

        # Instructions
        if self.state == STATE_AIMING:
            help_text = self.make_text("CLICK to shoot  |  RIGHT-CLICK to swap", (120, 120, 120), 14)
            self.screen.blit(help_text, (SHOOTER_X - help_text.get_width() // 2, SHOOTER_Y + 20))

    def _draw_overlay(self, title, subtitle):
        """Draw game over or win overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((640, 360), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Title
        title_text = self.make_text(title, (255, 255, 255), 60)
        title_rect = title_text.get_rect(center=(320, 140))
        self.screen.blit(title_text, title_rect)

        # Score
        score_text = self.make_text(f"SCORE: {self.score}", (255, 220, 100), 40)
        score_rect = score_text.get_rect(center=(320, 200))
        self.screen.blit(score_text, score_rect)

        # Subtitle
        sub_text = self.make_text(subtitle, (180, 180, 180), 20)
        sub_rect = sub_text.get_rect(center=(320, 260))
        self.screen.blit(sub_text, sub_rect)
