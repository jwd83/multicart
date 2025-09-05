import pygame
from scene import Scene
from utils import *
import numpy as np
import math
import settings
import threading

# Adapted from the following code:
# https://github.com/Apsis/Synthetic-Programming


class Julia(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.w = settings.RESOLUTION[0]
        self.h = settings.RESOLUTION[1]

        self.draw_a = True

        self.drawing = False

        # make 2 frames to switch between, one to be drawing on and one to be displaying
        self.frame_a = pygame.Surface((self.w, self.h))
        self.frame_b = pygame.Surface((self.w, self.h))

        self.frame_a.fill((0, 0, 0))
        self.frame_b.fill((0, 0, 0))

        self.standard_font_size = 10
        # self.f_text = self.Text("", (10, 10))
        
        # Precompute constants for better performance
        self.max_iter = 51
        self.escape_radius = 10.0
        self.escape_radius_squared = self.escape_radius * self.escape_radius
        
        self.update_f()

    def update_f(self):
        t = self.elapsed() / 3
        self.f = math.sin(t)
        self.cx = math.cos(t / 7)

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        if not self.drawing:
            self.drawing = True
            threading.Thread(target=self.render_julia_set).start()

        if self.draw_a:
            self.screen.blit(self.frame_a, (0, 0))
        else:
            self.screen.blit(self.frame_b, (0, 0))

    def render_julia_set(self):
        # self.log("Rendering Julia Set")
        self.update_f()

        self.julia_set = generate_julia(
            settings.RESOLUTION[1], settings.RESOLUTION[0], self.f, self.cx,
            max_iter=self.max_iter, escape_radius=self.escape_radius
        )

        # update the frame we are not currently drawing on
        if self.draw_a:
            draw_julia_set(self.frame_b, self.julia_set)
        else:
            draw_julia_set(self.frame_a, self.julia_set)

        self.draw_a = not self.draw_a
        self.drawing = False

    def draw_old(self):
        self.screen.fill((0, 0, 0))
        self.update_f()

        self.julia_set = generate_julia(
            settings.RESOLUTION[1], settings.RESOLUTION[0], self.f, self.cx
        )

        # Draw the surface on the screen
        draw_julia_set(self.screen, self.julia_set)

        # self.draw_text()


def draw_julia_set(screen, julia_set):
    # Convert numpy array to Pygame surface
    # pygame expects arrays in (width, height) format, so we need to transpose
    surface = pygame.surfarray.make_surface(julia_set.T)
    
    # Draw the surface on the screen
    screen.blit(surface, (0, 0))


def generate_julia(h, w, f, cx, max_iter=51, escape_radius=10.0):
    """
    Generate Julia set using vectorized numpy operations for much better performance.
    This replaces the nested loops with vectorized operations that leverage numpy's C backend.
    """
    re_min = -2.0
    re_max = 2.0
    im_min = -2.0
    im_max = 2.0
    
    # Create coordinate grids using meshgrid for vectorization
    re = np.linspace(re_min, re_max, w)
    im = np.linspace(im_max, im_min, h)
    Re, Im = np.meshgrid(re, im)
    
    # Convert to complex numbers
    z = Re + 1j * Im
    c = complex(cx, f)
    
    # Initialize the result array - make sure it's the right shape and type for pygame
    julia_set = np.zeros((h, w), dtype=np.uint8)
    
    # Vectorized Julia set calculation
    # Process in chunks to balance memory usage and performance
    chunk_size = min(1000, max(h, w) // 4)  # Adaptive chunk size
    
    for i in range(0, h, chunk_size):
        end_i = min(i + chunk_size, h)
        for j in range(0, w, chunk_size):
            end_j = min(j + chunk_size, w)
            
            # Extract chunk
            z_chunk = z[i:end_i, j:end_j].copy()
            result_chunk = np.full(z_chunk.shape, 255, dtype=np.uint8)
            
            # Vectorized iteration with early termination optimization
            for n in range(max_iter):
                # Check which points are still in the set using squared magnitude for speed
                abs_squared = z_chunk.real * z_chunk.real + z_chunk.imag * z_chunk.imag
                mask = abs_squared < escape_radius * escape_radius
                
                if not np.any(mask):
                    break
                    
                # Update only the points that are still in the set
                z_chunk[mask] = z_chunk[mask] * z_chunk[mask] + c
                result_chunk[mask] = 255 - n * 5
                
            # Store the result
            julia_set[i:end_i, j:end_j] = result_chunk
    
    return julia_set
