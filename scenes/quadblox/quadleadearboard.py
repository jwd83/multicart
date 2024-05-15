import pygame
from scene import Scene
from utils import *
import threading
import requests


class QuadLeaderboard(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.game.scene_push_under = "Plasma"

        self.leaderboard = None

        self.thread_get_leaderboard = threading.Thread(
            target=self.thread_get_leaderboard
        )
        self.thread_get_leaderboard.start()

        self.texts = [
            self.standard_text("Leaderboard", 40),
            self.standard_text("Fetching...", 20),
        ]

    def thread_get_leaderboard(self):
        self.log("thread_get_leaderboard starting")

        server = self.game.config["main"]["server"]

        try:
            j = requests.get(f"{server}/leaderboard").json()
            self.log(j)
            new_texts = [self.standard_text("Leaderboard", 40)]
            for i, score in enumerate(j):
                new_texts.append(
                    self.standard_text(
                        f"{i+1}. {score['player']} - {score['time']:.3f} - {score['frames']}",
                        20,
                    )
                )
            self.texts = new_texts
            self.leaderboard = j
        except Exception as e:
            self.log("thread_get_leaderboard error: " + str(e))

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        # draw the first text in the list at the top center
        self.blit_centered(self.texts[0], self.screen, (0.5, 0.05))

        # draw the rest of the text in the list spaced 20 px apart

        for i, text in enumerate(self.texts[1:]):
            self.screen.blit(text, (20, 100 + i * 20))
