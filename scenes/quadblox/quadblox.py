import pygame
from scene import Scene
from utils import *
from .scripts.qb import Board, colors, Piece, Shapes, QBMode
import copy
import settings
import threading
import requests
import time
import os


class BoxParticle(pygame.sprite.Sprite):
    def __init__(self, row, col, color, board: Board):
        super().__init__()

        self.alpha = random.randint(64, 64 * 3)

        self.image = pygame.Surface(
            (board.block_size, board.block_size)
        ).convert_alpha()
        self.image.set_alpha(self.alpha)
        self.speed = (random.uniform(-0.25, 0.25), random.uniform(-1.5, -0.5))
        self.image.fill(colors[color])
        self.rect = self.image.get_rect()
        tlx = board.pos[0] + board.block_size * col
        tly = board.pos[1] + board.block_size * row
        self.rect.topleft = (tlx, tly)

    def update(self):
        self.alpha -= 3
        if self.alpha <= 0:
            self.kill()
            return
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]
        self.image.set_alpha(self.alpha)


class QuadBlox(Scene):

    def __init__(self, game):
        super().__init__(game)

        self.particle_group = pygame.sprite.Group()

        self.client_run = True

        self.game_number = 0
        self.board_number = 0

        self.player_board = Board((100, 10))
        self.player_board.clear()

        self.opponents = [Board() for _ in range(8)]
        self.setup_opponents()

        self.piece_queue = []

        # start populating the queue
        self.open_bag()
        self.open_bag()

        self.player_piece = self.next_piece_in_queue()
        self.next_piece = self.next_piece_in_queue()
        self.stored_piece = None

        self.drop_at = self.player_board.level_speed()
        self.drop_count = 0

        self.das_startup_frames = 16
        self.das_interval_frames = 6
        self.held_down_for = 0
        self.held_left_for = 0
        self.held_right_for = 0

        self.died_at = 0
        self.died_frame = 0
        self.high_score = None

        self.standard_font_size = 20
        # self.standard_stroke = False
        self.standard_stroke = True
        self.standard_stroke_color = (0, 0, 0)
        self.standard_stroke_thickness = 1

        self.projected_piece = None

        self.texts = {}
        self.create_text_fields()

        # record our starting frame
        self.start_frame = self.game.frame_count()

        # check if we have a prior client thread running from a re-init
        if hasattr(self, "game_client"):
            self.log("terminating prior client thread...")
            self.shutdown_client()
            self.log("client thread terminated.")

        if self.game.qb_mode == QBMode.Multiplayer:
            # kick off the client thread
            self.client_run = True
            self.game_client = threading.Thread(target=self.client_thread)
            self.game_client.start()

    def create_text_fields(self):

        pos = self.player_board.pos
        bs = self.player_board.block_size

        self.texts["blocks"] = self.Text(
            "blocks", (settings.RESOLUTION[0] // 2, 10 + 40 * 2)
        )
        self.texts["bpm"] = self.Text(
            "blox/min", (settings.RESOLUTION[0] // 2, 10 + 40 * 3)
        )
        self.texts["clears"] = self.Text("clears", (pos[0] + bs * 11, pos[1] + 20))
        self.texts["das"] = self.Text(
            f"das [l:d:r] {self.das_startup_frames}>>{self.das_interval_frames}]",
            (settings.RESOLUTION[0] // 2, 10 + 40 * 6),
        )
        self.texts["frames"] = self.Text(
            "frames", (settings.RESOLUTION[0] // 2, 10 + 40 * 1)
        )
        self.texts["level"] = self.Text(
            "level", (pos[0] + bs * 11, pos[1] + 40 + 8 * 20)
        )
        self.texts["lines"] = self.Text(
            "lines", (pos[0] + bs * 11, pos[1] + 40 + 6 * 20)
        )
        self.texts["lpm"] = self.Text(
            "lines/min", (settings.RESOLUTION[0] // 2, 10 + 40 * 4)
        )
        self.texts["next_piece"] = self.Text("next", (10, 90))
        self.texts["next"] = self.Text(
            "next", (pos[0] + bs * 11, pos[1] + 40 + 10 * 20)
        )
        self.texts["speed"] = self.Text(
            "drop speed", (settings.RESOLUTION[0] // 2, 10 + 40 * 5)
        )
        self.texts["stored"] = self.Text("stored", (10, 10))
        self.texts["time"] = self.Text(
            "time", (settings.RESOLUTION[0] // 2, 10 + 40 * 0)
        )

        self.texts["points"] = self.Text(
            str(self.player_board.points), (pos[0] + bs * 11, pos[1])
        )
        for y in range(4):
            self.texts[f"clears{y}"] = self.Text(
                f"{y + 1}x " + str(self.player_board.clears[y]),
                (pos[0] + bs * 11, pos[1] + 40 + y * 20),
            )
        self.texts["lines_cleared"] = self.Text(
            str(self.player_board.lines_cleared),
            (pos[0] + bs * 11, pos[1] + 40 + 7 * 20),
        )
        self.texts["level"] = self.Text(
            str(self.player_board.level),
            (pos[0] + bs * 11, pos[1] + 40 + 9 * 20),
        )
        self.texts["next_level"] = self.Text(
            str(self.player_board.next_level),
            (pos[0] + bs * 11, pos[1] + 40 + 11 * 20),
        )

    def shutdown_client(self):
        self.client_run = False
        self.game_client.join()

    def high_score_thread(self):
        self.log("high score thread: starting")

        try:

            # check if we have a high score to send in and clear it back to None
            if self.high_score is not None:

                server = self.game.config["main"]["server"]

                hs_url = f"{server}/leaderboard?"
                hs_url += f"player={self.high_score['player']}&"
                hs_url += f"time={self.high_score['time']}&"
                hs_url += f"lines={self.high_score['lines']}&"
                hs_url += f"pieces={self.high_score['pieces']}&"
                hs_url += f"score={self.high_score['score']}&"
                hs_url += f"frames={self.high_score['frames']}"

                self.log(f"client thread: sending high score: {hs_url}")

                requests.post(hs_url)

                self.high_score = None
        except:
            self.log("high score thread: something went wrong")
            pass

    def client_thread(self):
        self.log("client thread: starting")

        server = self.game.config["main"]["server"]

        self.log(f"client thread: server set to {server}")

        r = requests.get(f"{server}/games/0/sit").json()
        self.board_number = r["seat"]

        self.log(f"client thread: sitting at seat {self.board_number}")

        while self.client_run:
            try:
                # SLEEP
                time.sleep(0.5)

                # UPDATE OPPONENTS
                self.log("client thread: updating opponents")
                r = requests.get(f"{server}/games/{self.game_number}")
                # self.log(r.text)

                board_to_update = 0
                for i, board_state in enumerate(r.json()):
                    # skip our board
                    if i == self.board_number:
                        continue

                    # update the board
                    if board_to_update < len(self.opponents):
                        self.opponents[board_to_update].import_board(board_state)

                    # increment the board to update
                    board_to_update += 1

                # UPDATE OUR BOARD
                self.log(f"client thread: updating our board {self.board_number}")
                r = requests.post(
                    f"{server}/games/update/{self.game_number}/{self.board_number}?board_state={self.player_board.export_board()}"
                )

                # SEND ATTACKS
                if self.player_board.outgoing_attack_queue > 0:
                    # sample this incase there is a thread/race sync issue
                    attacks = self.player_board.outgoing_attack_queue
                    # deduct the pending attacks from our board
                    self.player_board.outgoing_attack_queue -= attacks

                    # write the attack to the server
                    r = requests.post(
                        f"{server}/games/line-clear-attack/{self.game_number}/{self.board_number}/{attacks}"
                    )

                    self.log(r.json)

                # IF DEAD CAN STOP HERE
                if self.died_at:
                    continue

                # GET ATTACKS
                r = requests.get(
                    f"{server}/games/get-attacks/{self.game_number}/{self.board_number}"
                ).json()
                self.log(f"got {r['lines']} attacks")
                if r["lines"] > 0:
                    self.player_board.add_line_to_bottom(r["lines"])

            except:
                self.log("something went wrong")
                pass

        self.log("client thread: shutting down")

    def open_bag(self, num_bags=1):

        for _ in range(num_bags):

            bag = [
                Shapes.I,
                Shapes.J,
                Shapes.L,
                Shapes.O,
                Shapes.S,
                Shapes.T,
                Shapes.Z,
            ]

            random.shuffle(bag)

            for shape in bag:
                self.piece_queue.append(Piece(shape))

    def next_piece_in_queue(self):
        # restock the queue if we are running low
        while len(self.piece_queue) < 10:
            self.open_bag()

        # return the next piece
        return self.piece_queue.pop(0)

    def setup_opponents(self):
        for opponent in self.opponents:
            # opponent.clear()

            # setup to draw opponent boards
            obs = 6
            opponent.block_size = obs

            x_step = obs * 11

            y1 = 10
            y2 = y1 + 28 * obs

            x = 640 / 2
            y = y1

            for i, opponent in enumerate(self.opponents):

                opponent.pos = (x, y)

                if i % 2 == 0:
                    y = y2
                else:
                    y = y1
                    x += x_step

    def update_player(self):

        # check for death
        self.check_for_death()

        # if we are dead stop the update logic here
        if self.died_at:
            return

        # check if we are already colliding. If we are, place the piece
        if self.player_piece.collides(self.player_board):
            self.place()
            return

        # developer mode
        if settings.DEBUG:
            if pygame.K_i in self.game.just_pressed:
                self.player_piece = Piece(Shapes.I)
            if pygame.K_a in self.game.just_pressed:
                self.player_board.add_line_to_bottom()

        # check to swap piece
        if pygame.K_TAB in self.game.just_pressed:
            # swap the piece
            if self.stored_piece is None:
                self.log("Storing first piece")
                self.stored_piece = self.player_piece
                self.player_piece = self.next_piece
                self.next_piece = self.next_piece_in_queue()
            else:
                self.log("Swapping stored piece")
                self.player_piece, self.stored_piece = (
                    self.stored_piece,
                    self.player_piece,
                )

            # TODO: if there is a collision swap back (needs fixes with bounds checking/collision checking)
            # if self.player_piece.collides(self.player_board):
            #     print("The piece collided with the board, swapping back")
            #     self.player_piece, self.stored_piece = self.stored_piece, self.player_piece

            # set the new piece to the stored location
            self.player_piece.x = 3
            self.player_piece.y = 0

        # LEFT / RIGHT MOVEMENT
        left_held_tick = False
        right_held_tick = False

        # if player is holding both left and right reset the held counters
        if self.game.pressed[pygame.K_LEFT] and self.game.pressed[pygame.K_RIGHT]:
            self.held_left_for = 0
            self.held_right_for = 0
        else:
            # left hold
            if self.game.pressed[pygame.K_LEFT]:
                self.held_left_for += 1
                if self.held_left_for >= self.das_startup_frames:
                    if (
                        self.held_left_for - self.das_startup_frames
                    ) % self.das_interval_frames == 0:
                        left_held_tick = True
            else:
                self.held_left_for = 0

            # right hold
            if self.game.pressed[pygame.K_RIGHT]:
                self.held_right_for += 1
                if self.held_right_for >= self.das_startup_frames:
                    if (
                        self.held_right_for - self.das_startup_frames
                    ) % self.das_interval_frames == 0:
                        right_held_tick = True
            else:
                self.held_right_for = 0

        sim_left_right = copy.deepcopy(self.player_piece)
        if pygame.K_LEFT in self.game.just_pressed or left_held_tick:
            sim_left_right.x -= 1

        if pygame.K_RIGHT in self.game.just_pressed or right_held_tick:
            sim_left_right.x += 1

        # if the sim piece does not collide update our piece to it
        if not sim_left_right.collides(self.player_board):
            self.player_piece = sim_left_right

        # ROTATION
        sim_rotate = copy.deepcopy(self.player_piece)

        if pygame.K_UP in self.game.just_pressed:
            sim_rotate.rotate()
            if not sim_rotate.collides(self.player_board):
                self.player_piece = sim_rotate
            else:
                # try right one first
                sim_rotate.x = self.player_piece.x + 1

                if not sim_rotate.collides(self.player_board):
                    self.player_piece = sim_rotate
                else:
                    # try left one if that didn't work
                    sim_rotate.x = self.player_piece.x - 1

                    if not sim_rotate.collides(self.player_board):
                        self.player_piece = sim_rotate
                    else:
                        # for an i piece try 2 left
                        if sim_rotate.shape == Shapes.I:

                            # try left two (from the original piece)
                            sim_rotate.x = self.player_piece.x - 2
                            if not sim_rotate.collides(self.player_board):
                                self.player_piece = sim_rotate

        # DOWN MOVEMENT / GRAVITY
        # should we fall this frame?
        try_drop = False
        user_drop = False

        # check if down has been held for a while
        if self.game.pressed[pygame.K_DOWN]:
            self.held_down_for += 1
            if self.held_down_for >= self.das_startup_frames:
                if (
                    self.held_down_for - self.das_startup_frames
                ) % self.das_interval_frames == 0:
                    try_drop = True
                    user_drop = True

        else:
            self.held_down_for = 0

        # check for key press down
        if pygame.K_DOWN in self.game.just_pressed:
            try_drop = True
            user_drop = True

        # if the user commands a down, increment the points by 1
        if user_drop:
            self.player_board.points += 1

        # increment drop count and see if we need to drop the piece
        self.drop_count += 1
        if self.drop_count >= self.drop_at:
            try_drop = True

        # perform the drop if needed
        if try_drop:

            # if we are dropping the piece, reset the drop count
            self.drop_count = 0
            sim_drop = copy.deepcopy(self.player_piece)
            sim_drop.y += 1
            if not sim_drop.collides(self.player_board):
                self.player_piece = sim_drop
            else:
                self.place()

        # solve projected piece and move to it if commanded to
        projected = copy.deepcopy(self.player_piece)
        while not projected.collides(self.player_board):
            projected.y += 1

        projected.y -= 1

        if projected.y > self.player_piece.y:
            self.projected_piece = projected
            if pygame.K_SPACE in self.game.just_pressed:
                self.drop_count = 0
                self.player_board.points += self.projected_piece.y - self.player_piece.y
                self.player_piece = self.projected_piece
        else:
            self.projected_piece = None

        # check for death
        self.check_for_death()

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            return

        # handle the main player input
        self.update_player()

        # update particle effects
        self.particle_group.update()

        # check for end of 40 line rush if we are still alive
        if not self.died_frame:
            if (
                self.game.qb_mode == QBMode.SoloForty
                and self.player_board.lines_cleared >= 40
            ):
                self.kill_player()

                self.high_score = {
                    "player": os.getlogin(),
                    "time": (self.died_frame - self.start_frame) * 1.0 / 60.0,
                    "lines": self.player_board.lines_cleared,
                    "pieces": self.player_board.blocks_placed,
                    "score": self.player_board.points,
                    "frames": self.died_frame - self.start_frame,
                }

                self.high_score_client = threading.Thread(target=self.high_score_thread)
                self.high_score_client.start()

    def check_for_death(self):
        if self.died_at:
            return

        # check for death
        for x in range(10):
            for y in range(4):
                if self.player_board.grid[y][x]:
                    self.kill_player()

    def kill_player(self):
        self.died_at = self.elapsed()
        self.died_frame = self.game.frame_count()
        self.player_board.kill()
        self.projected_piece = None

    def place(self):
        self.log(f"Placing piece: {self.player_piece.shape}")
        # place the current piece and get a new piece
        results = self.player_board.place(self.player_piece)
        self.drop_at = self.player_board.level_speed()
        self.player_piece = self.next_piece
        self.next_piece = self.next_piece_in_queue()
        # restart the delay for down being held to slow up the next place pieced
        # from dropping right away when just placed
        self.held_down_for = 0

        if len(results):
            # self.log(f"Lines cleared: {len(lines_cleared)} {lines_cleared}")
            clear_sound = ""
            if len(results) == 4:
                # todo: get a better sound for this
                clear_sound = "level-up-bonus-sequence-3-186892"
            elif len(results) == 3:
                clear_sound = "level-up-bonus-sequence-3-186892"
            elif len(results) == 2:
                clear_sound = "level-up-bonus-sequence-2-186891"
            else:
                clear_sound = "level-up-bonus-sequence-1-186890"

            # generate particles for the cleared lines
            for row in results:
                for col in range(10):
                    for _ in range(len(results)):
                        self.particle_group.add(
                            BoxParticle(
                                row["row"], col, row["blocks"][col], self.player_board
                            )
                        )

            # self.play_sound("jsfxr-qb-lines-explode")
            self.play_sound(clear_sound)
        else:
            self.play_sound("jsfxr-drop2")

    def draw_projected_piece(self):
        if self.projected_piece is not None:
            for x in range(4):
                for y in range(4):
                    if self.projected_piece.grid[y][x]:
                        pygame.draw.rect(
                            self.screen,
                            (140, 140, 140),
                            (
                                (self.projected_piece.x + x) * 12 + 100,
                                (self.projected_piece.y + y) * 12
                                + 10
                                + math.sin(self.elapsed() * 12) * 2,
                                12 - 1,
                                12 - 1,
                            ),
                        )

    def draw(self):

        # plasma scene will handle filling the background back up

        # draw the player board
        self.draw_player_board()

        # draw the opponents in multiplayer mode
        if self.game.qb_mode == QBMode.Multiplayer:

            # draw the multiplayer opponents
            self.draw_opponents()

        else:
            # draw the single player stuff
            self.draw_solo_stats()

        # draw the particle effects

        self.particle_group.draw(self.screen)

    def draw_texts(self):

        self.texts["points"].text = str(self.player_board.points)
        for y in range(4):
            self.texts[f"clears{y}"].text = f"{y + 1}x {self.player_board.clears[y]}"
        self.texts["lines_cleared"].text = str(self.player_board.lines_cleared)
        self.texts["level"].text = str(self.player_board.level)
        self.texts["next_level"].text = str(self.player_board.next_level)

        # for text in self.texts.values():
        #     text.draw()
        self.all_text.draw(self.screen)

    def draw_player_board(self):
        self.draw_board(self.player_board)
        self.draw_projected_piece()

        self.draw_texts()

        # draw our piece
        self.draw_piece()

        # draw the next piece
        self.draw_next_piece()

        # draw stored piece
        self.draw_stored_piece()

        # draw the piece queue
        self.draw_piece_queue()

    def draw_opponents(self):

        # draw the opponents boards
        for opponent in self.opponents:
            self.draw_board(opponent)

    def draw_arbitrary_piece(self, piece: Piece, pos=(0, 0), size: int = 12):
        for x in range(4):
            for y in range(4):
                if piece.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        colors[piece.color],
                        (pos[0] + size * x, pos[1] + size * y, size - 1, size - 1),
                    )

    def draw_piece_queue(self):
        y = 160

        for i, piece in enumerate(self.piece_queue):
            self.draw_arbitrary_piece(piece, (10, y, 10 - i), 10 - i)
            y += 5 * (10 - i)

    def draw_stored_piece(self):
        if self.stored_piece is not None:
            self.draw_arbitrary_piece(self.stored_piece, (10, 30))

    def draw_next_piece(self):
        self.draw_arbitrary_piece(self.next_piece, (10, 110))

    def draw_piece(self):
        for x in range(4):
            for y in range(4):
                if self.player_piece.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        colors[self.player_piece.color],
                        (
                            (self.player_piece.x + x) * 12 + 100,
                            (self.player_piece.y + y) * 12 + 10,
                            12 - 1,
                            12 - 1,
                        ),
                    )

    def draw_board(self, board: Board):
        pos = board.pos
        bs = board.block_size

        # draw a black background for the board
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (pos[0] - 1, pos[1] - 1, 10 * bs + 1, 24 * bs + 1),
        )

        # check if we are in a 40 line rush mode
        if self.game.qb_mode == QBMode.SoloForty:

            # draw this in the top center of the board

            self.blit_centered(
                self.make_text(
                    text=f"{40 - self.player_board.lines_cleared}",
                    color=(90, 90, 90),
                    fontSize=80,
                ),
                self.screen,
                (0.25, 0.09),
            )

        # draw a red horizontal line after the first 4 rows
        pygame.draw.line(
            self.screen,
            (255, 0, 0),
            (pos[0], pos[1] + 4 * bs - 1),
            (pos[0] + 10 * bs - 1, pos[1] + 4 * bs - 1),
        )

        # draw the board
        for y, row in enumerate(board.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        colors[cell],
                        (pos[0] + x * bs, pos[1] + y * bs, bs - 1, bs - 1),
                    )

        # draw a grey border around the board
        border_width = 4
        pygame.draw.rect(
            surface=self.screen,
            color=(128, 128, 128),
            rect=(
                pos[0] - border_width - 1,
                pos[1] - border_width - 1,
                10 * bs + 2 * border_width + 1,
                24 * bs + 2 * border_width + 1,
            ),
            width=border_width,
        )

    def quit(self):
        self.log("shutting down client thread...")
        self.shutdown_client()
        self.log("client thread terminated.")

    def draw_solo_stats(self):

        # format elapsed time to a string with 3 decimal places
        # real_time = f"{self.elapsed():.3f}"

        if self.died_frame:
            fr = self.died_frame - self.start_frame
        else:
            fr = self.game.frame_count() - self.start_frame
        et = fr * 1.0 / 60.0

        lpm = 0
        bpm = 0

        if fr > 0:
            bpm = self.player_board.blocks_placed / et * 60
            lpm = self.player_board.lines_cleared / et * 60

        dl = 0
        dd = 0
        dr = 0

        if self.held_left_for >= self.das_startup_frames:
            dl = (
                self.held_left_for - self.das_startup_frames
            ) % self.das_interval_frames
        else:
            dl = self.held_left_for

        if self.held_down_for >= self.das_startup_frames:
            dd = (
                self.held_down_for - self.das_startup_frames
            ) % self.das_interval_frames
        else:
            dd = self.held_down_for

        if self.held_right_for >= self.das_startup_frames:
            dr = (
                self.held_right_for - self.das_startup_frames
            ) % self.das_interval_frames
        else:
            dr = self.held_right_for

        x = settings.RESOLUTION[0] // 2
        y = 30

        # build the fast texts if they don't exist
        if "solo_time" not in self.texts:
            self.texts["solo_time"] = self.Text(f"{et:.3f}", (x, y))
            y += 40

            self.texts["solo_frames"] = self.Text(f"{fr}", (x, y))
            y += 40

            self.texts["solo_blocks_placed"] = self.Text(
                str(self.player_board.blocks_placed), (x, y)
            )
            y += 40

            self.texts["solo_bpm"] = self.Text(f"{bpm:.1f}", (x, y))
            y += 40

            self.texts["solo_lpm"] = self.Text(f"{lpm:.1f}", (x, y))
            y += 40

            self.texts["solo_drop"] = self.Text(
                f"{self.drop_at} : {self.drop_count}", (x, y)
            )
            y += 40

            self.texts["solo_das"] = self.Text(f"{dl} : {dd} : {dr}", (x, y))

        else:
            # update the fast texts
            self.texts["solo_time"].text = f"{et:.3f}"
            self.texts["solo_frames"].text = f"{fr}"
            self.texts["solo_blocks_placed"].text = str(self.player_board.blocks_placed)
            self.texts["solo_bpm"].text = f"{bpm:.1f}"
            self.texts["solo_lpm"].text = f"{lpm:.1f}"
            self.texts["solo_drop"].text = f"{self.drop_at} : {self.drop_count}"
            self.texts["solo_das"].text = f"{dl} : {dd} : {dr}"
