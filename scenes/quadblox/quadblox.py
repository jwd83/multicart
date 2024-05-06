import pygame
from scene import Scene
from utils import *
from .scripts.qb import Board, colors, Piece, Shapes
import copy
import settings


class QuadBlox(Scene):
    def __init__(self, game):
        super().__init__(game)


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

        self.drop_at = 60 # frames per line fall
        self.drop_count = 0

        self.held_down_for = 0
        self.held_toggles_at = 10
        self.held_frame_interval = 4
        self.held_left_for = 0
        self.held_right_for = 0

        self.died_at = 0

        self.level = 0

        self.standard_font_size = 20
        self.standard_stroke = False

        self.projected_piece = None

    def open_bag(self, num_bags = 1):

        for j in range(num_bags):

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


    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            return


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
                self.player_piece, self.stored_piece = self.stored_piece, self.player_piece

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

        # if they are holding both reset it
        if self.game.pressed[pygame.K_LEFT] and self.game.pressed[pygame.K_RIGHT]:
            self.held_left_for = 0
            self.held_right_for = 0


        # check if left has been held for a while
        if not self.game.pressed[pygame.K_LEFT]:
            self.held_left_for = 0
        else:
            self.held_left_for += 1

            if self.held_left_for >= self.held_toggles_at:
                numerator = self.held_left_for - self.held_toggles_at
                denominator = self.held_frame_interval

                if numerator % denominator == 0:
                    left_held_tick = True


        if not self.game.pressed[pygame.K_RIGHT]:
            self.held_right_for = 0
        else:
            self.held_right_for += 1

            if self.held_right_for >= self.held_toggles_at:
                numerator = self.held_right_for - self.held_toggles_at
                denominator = self.held_frame_interval

                if numerator % denominator == 0:
                    right_held_tick = True


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

        # check if down has been held for a while
        if self.game.pressed[pygame.K_DOWN]:
            self.held_down_for += 1
            if self.held_down_for >= self.held_toggles_at:
                numerator = self.held_down_for - self.held_toggles_at
                denominator = self.held_frame_interval

                if numerator % denominator == 0:
                    try_drop = True
        else:
            self.held_down_for = 0

        # check for key press down
        if pygame.K_DOWN in self.game.just_pressed:
            try_drop = True


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
        else:
            self.projected_piece = None

        if pygame.K_SPACE in self.game.just_pressed and self.projected_piece is not None:
            self.drop_count = 0
            self.player_piece = self.projected_piece

        # check for death
        for x in range(10):
            for y in range(4):
                if self.player_board.grid[y][x]:
                    self.died_at = self.elapsed
                    self.player_board.kill()
                    self.projected_piece = None
                    return

    def place(self):
        self.game.log(f"Placing piece: {self.player_piece.shape}")
        # place the current piece and get a new piece
        self.player_board.place(self.player_piece)
        self.level = self.player_board.lines_cleared // 10
        self.drop_at = max(4, 60 - self.level * 5)
        self.player_piece = self.next_piece
        self.next_piece = self.next_piece_in_queue()
        # restart the delay for down being held to slow up the next place pieced
        # from dropping right away when just placed
        self.held_down_for = 0

        if random.choice([True, False]):
            self.play_sound("jsfxr-drop2")
        else:
            self.play_sound("jsfxr-drop2")

    def draw_projected_piece(self):
        if self.projected_piece is not None:
            for x in range(4):
                for y in range(4):
                    if self.projected_piece.grid[y][x]:
                        pygame.draw.rect(
                            self.screen,
                            (140,140,140),
                            (
                                (self.projected_piece.x + x) * 12 + 100,
                                (self.projected_piece.y + y) * 12 + 10 + math.sin(self.elapsed() * 12) * 2,
                                12 - 1,
                                12 - 1)
                        )

    def draw(self):

        # draw the player board
        self.screen.fill((0, 0, 0))
        self.draw_board(self.player_board)
        self.draw_projected_piece()

        # draw the player stats
        pos = self.player_board.pos
        bs = self.player_board.block_size

        self.screen.blit(
            self.standard_text( str(self.player_board.points)),
            (pos[0] + bs * 11, pos[1])
        )

        self.screen.blit(
            self.standard_text("CLEARS"),
            (pos[0] + bs * 11, pos[1] + 20)
        )

        for y in range(4):
            self.screen.blit(
                self.standard_text(f"{y + 1}x " + str(self.player_board.clears[y])),
                (pos[0] + bs * 11, pos[1] + 40 + y * 20)
            )

        self.screen.blit(
            self.standard_text("LINES"),
            (pos[0] + bs * 11, pos[1] + 40 + 6 * 20)
        )

        self.screen.blit(
            self.standard_text(str(self.player_board.lines_cleared)),
            (pos[0] + bs * 11, pos[1] + 40 + 7 * 20)
        )

        self.screen.blit(
            self.standard_text("LEVEL"),
            (pos[0] + bs * 11, pos[1] + 40 + 8 * 20)
        )

        self.screen.blit(
            self.standard_text(str(self.level)),
            (pos[0] + bs * 11, pos[1] + 40 + 9 * 20)
        )

        # draw the opponents boards
        for opponent in self.opponents:
            self.draw_board(opponent)

        # draw our piece
        self.draw_piece()

        # draw the next piece
        self.draw_next_piece()

        # draw stored piece
        self.draw_stored_piece()

        # draw the piece queue
        self.draw_piece_queue()


    def draw_arbitrary_piece(self, piece : Piece, pos = (0,0), size: int = 12):
        for x in range(4):
            for y in range(4):
                if piece.grid[y][x]:
                    pygame.draw.rect(
                        self.screen,
                        colors[piece.color],
                        (
                            pos[0] + size * x,
                            pos[1] + size * y,
                            size - 1,
                            size - 1)
                    )

    def draw_piece_queue(self):
        y = 160

        for i, piece in enumerate(self.piece_queue):
            self.draw_arbitrary_piece(piece, (10, y, 10 - i), 10 - i)
            y += 5 * (10 - i)

    def draw_stored_piece(self):
        self.screen.blit(
            self.standard_text("STORED"),
            (10, 10)
        )
        if self.stored_piece is not None:
            self.draw_arbitrary_piece(self.stored_piece, (10, 30))


    def draw_next_piece(self):
        self.screen.blit(
            self.standard_text("NEXT"),
            (10, 90)
        )
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
                            12 - 1)
                    )

    def draw_board(self, board: Board):
        pos = board.pos
        bs = board.block_size

        # draw a red horizontal line after the first 4 rows
        pygame.draw.line(
            self.screen,
            (255, 0, 0),
            (pos[0], pos[1] + 4 * bs-1),
            (pos[0] + 10 * bs -1, pos[1] + 4 * bs -1)
        )

        # draw the board
        for y, row in enumerate(board.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        colors[cell],
                        (
                            pos[0] + x * bs,
                            pos[1] + y * bs,
                            bs - 1,
                            bs - 1)
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
                24 * bs + 2 * border_width + 1
            ),
            width=border_width
        )


