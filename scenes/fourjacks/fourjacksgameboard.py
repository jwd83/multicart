import pygame
from scene import Scene
import random
import settings
from copy import deepcopy


class FourJacksGameBoard(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.key_color = (123, 231, 132)  # some random garbage color
        self.board = pygame.Surface((400, 280)).convert()
        self.board.set_colorkey(self.key_color)
        self.board.fill((33, 33, 255))
        self.colors = ["RED", "YELLOW"]
        self.current_turn = 0
        self.ai_delay_start = 0
        self.ai_delay_total = 0.2
        self.ai_first_turn = True
        self.last_ai_move = ""

        rows, cols = (6, 7)
        self.board_map = [[0 for i in range(cols)] for j in range(rows)]
        self.board_score = self.score_board(self.board_map)

        self.selected_column = 0

        self.log(self.board_map)

    def update_player_turn(self):

        turn_change = self.current_turn

        # move the selected column
        if pygame.K_LEFT in self.game.just_pressed:
            self.selected_column -= 1
        if pygame.K_RIGHT in self.game.just_pressed:
            self.selected_column += 1

        # drop a piece
        if pygame.K_SPACE in self.game.just_pressed:
            col = self.selected_column
            row = 5
            searching = True

            while searching:
                if self.board_map[row][col] != 0:
                    row -= 1
                    if row < 0:
                        searching = False
                else:

                    self.board_map[row][col] = self.colors[self.current_turn]
                    self.board_score = self.score_board(self.board_map)
                    self.current_turn += 1
                    searching = False

        # pop a piece
        if pygame.K_RETURN in self.game.just_pressed:
            col = self.selected_column
            row = 5

            if self.board_map[row][col] == self.colors[self.current_turn]:
                while row > 0:
                    self.board_map[row][col] = self.board_map[row - 1][col]
                    row -= 1
                self.board_map[0][col] = 0
                self.board_score = self.score_board(self.board_map)

                self.current_turn += 1

        # check if the turn has changed
        if turn_change != self.current_turn:
            self.ai_delay_start = self.elapsed()

    def get_move_list(self, board, color):
        # create a possible list of 14 moves available
        # first 7 are drops and the second 7 are pops
        move_list = []

        for col in range(7):
            # check the top of each column to see if a piece can be dropped
            if board[0][col] == 0:
                move_list.append("d" + str(col))

            # check if we can pop a piece by checking the bottom of each column
            # to see if the bottom piece matches the color provided
            if board[5][col] == color:
                move_list.append("p" + str(col))

        return move_list

    def ai_turn_easy(self):
        # generate the list of possible moves this turn
        move_list = self.get_move_list(self.board_map, self.colors[self.current_turn])

        # chose a random element from the move list
        move = random.choice(move_list)

        # if the move is a drop
        if move[0] == "d":
            col = int(move[1])
            row = 5
            searching = True

            while searching:
                if self.board_map[row][col] != 0:
                    row -= 1
                    if row < 0:
                        searching = False
                else:
                    self.board_map[row][col] = self.colors[self.current_turn]
                    searching = False

        # if the move is a pop
        if move[0] == "p":
            col = int(move[1])
            row = 5

            while row > 0:
                self.board_map[row][col] = self.board_map[row - 1][col]
                row -= 1
            self.board_map[0][col] = 0

        self.board_score = self.score_board(self.board_map)
        self.current_turn += 1

    def ai_turn_hard(self):
        # generate the list of possible moves this turn
        move_list = self.get_move_list(self.board_map, self.colors[self.current_turn])

        # compute the minimax score for each move and record the best move
        best_move = None
        best_score = None

        self.log("Current Turn: " + str(self.current_turn))
        self.log("Move list: " + str(move_list))

        for move in move_list:
            new_board = deepcopy(self.board_map)
            self.apply_move_to_board(move, new_board, self.colors[self.current_turn])
            score = self.minimax(new_board, 4, self.current_turn == 1)
            self.log("Move: " + move + " Score: " + str(score))

            if best_move is None:
                best_move = move
                best_score = score

            if self.current_turn == 0:
                if score > best_score:
                    best_move = move
                    best_score = score
            else:
                if score < best_score:
                    best_move = move
                    best_score = score

        # apply the best move to the board
        self.apply_move_to_board(
            best_move, self.board_map, self.colors[self.current_turn]
        )
        self.board_score = self.score_board(self.board_map)
        self.current_turn += 1

    def apply_move_to_board(self, move, board, color):
        if move[0] == "d":
            col = int(move[1])
            row = 5
            searching = True

            while searching:
                if board[row][col] != 0:
                    row -= 1
                    if row < 0:
                        searching = False
                else:
                    board[row][col] = color
                    searching = False

        if move[0] == "p":
            col = int(move[1])
            row = 5

            while row > 0:
                board[row][col] = board[row - 1][col]
                row -= 1
            board[0][col] = 0

    def minimax(self, board, depth, maximizingPlayer):

        winner = self.board_winner(board)
        if winner is not None:
            if winner == "RED":
                return 1000000000000 * (depth + 1)
            else:
                return -1000000000000 * (depth + 1)

        if depth == 0:
            return self.summarize_board(board)

        if maximizingPlayer:
            maxEval = float("-inf")
            for move in self.get_move_list(board, "RED"):
                temp_board = deepcopy(board)
                self.apply_move_to_board(move, temp_board, "RED")
                eval = self.minimax(temp_board, depth - 1, False)
                maxEval = max(maxEval, eval)
            return maxEval
        else:
            minEval = float("inf")
            for move in self.get_move_list(board, "YELLOW"):
                temp_board = deepcopy(board)
                self.apply_move_to_board(move, temp_board, "YELLOW")
                eval = self.minimax(temp_board, depth - 1, True)
                minEval = min(minEval, eval)
            return minEval

    def update_ai_turn(self):
        # if the ai delay has not been reached, do nothing
        if self.elapsed() - self.ai_delay_start < self.ai_delay_total:
            return

        self.log(
            "AI Turn:"
            + str(self.current_turn)
            + " AI Easy: "
            + str(self.game.four_jacks_easy)
        )

        if self.ai_first_turn:
            self.ai_first_turn = False

            # ai should always drop on the middle column first turn
            self.selected_column = 3
            self.drop_piece(
                self.selected_column, self.colors[self.current_turn], self.board_map
            )
            self.board_score = self.score_board(self.board_map)
            self.current_turn += 1
            return

        if self.game.four_jacks_easy:
            self.ai_turn_easy()
        else:
            self.ai_turn_hard()

    def board_winner(self, board):
        # check for a horizontal win
        for row in range(6):
            for col in range(4):
                if (
                    board[row][col]
                    == board[row][col + 1]
                    == board[row][col + 2]
                    == board[row][col + 3]
                    != 0
                ):
                    return board[row][col]

        # check for a vertical win
        for row in range(3):
            for col in range(7):
                if (
                    board[row][col]
                    == board[row + 1][col]
                    == board[row + 2][col]
                    == board[row + 3][col]
                    != 0
                ):
                    return board[row][col]

        # check for a diagonal win
        for row in range(3):
            for col in range(4):
                if (
                    board[row][col]
                    == board[row + 1][col + 1]
                    == board[row + 2][col + 2]
                    == board[row + 3][col + 3]
                    != 0
                ):
                    return board[row][col]

        for row in range(3):
            for col in range(4):
                if (
                    board[row + 3][col]
                    == board[row + 2][col + 1]
                    == board[row + 1][col + 2]
                    == board[row][col + 3]
                    != 0
                ):
                    return board[row][col]

        return None

    def check_winner(self):
        player_1 = [0]
        player_2 = [0]

        # add up all game winning scores
        for row in range(6):
            for col in range(7):
                if self.board_score[row][col] >= 4:
                    if self.board_map[row][col] == self.colors[0]:
                        player_1.append(self.board_score[row][col])
                    else:
                        player_2.append(self.board_score[row][col])

        # sort player in descending order
        player_1.sort(reverse=True)
        player_2.sort(reverse=True)

        # did anyone have enough points to win?
        if player_1[0] >= 4 or player_2[0] >= 4:
            # if so, who won?

            # was there a tie?
            if player_1[0] == player_2[0]:
                self.game.winner = 2

            # did player 1 win?
            if player_1[0] > player_2[0]:
                self.game.winner = 0

            # did player 2 win?
            if player_1[0] < player_2[0]:
                self.game.winner = 1

    def drop_piece(self, col, color, board):
        row = 5
        searching = True

        while searching:
            if board[row][col] != 0:
                row -= 1
                if row < 0:
                    searching = False
            else:
                board[row][col] = color
                searching = False

    def pop_piece(self, col, board):
        row = 5

        while row > 0:
            board[row][col] = board[row - 1][col]
            row -= 1
        board[0][col] = 0

    def score_board(self, board):
        rows, cols = (6, 7)
        scores = [[0 for i in range(cols)] for j in range(rows)]
        for row in range(6):
            for col in range(7):
                if board[row][col] == 0:
                    scores[row][col] = 0
                else:
                    scores[row][col] = self.score_position(row, col, board)

        return scores

    # take in a board and return a summary of the board
    def summarize_board(self, board):
        rows, cols = (6, 7)
        total = 0

        weights = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]

        for row in range(rows):
            for col in range(cols):
                if board[row][col] == "RED":
                    total += weights[self.score_position(row, col, board)]
                if board[row][col] == "YELLOW":
                    total -= weights[self.score_position(row, col, board)]

        return total

    def score_position(self, row, col, board):
        score = 0

        score = max(self.score_horizontal(row, col, board), score)
        score = max(self.score_vertical(row, col, board), score)
        score = max(self.score_diagonal1(row, col, board), score)
        score = max(self.score_diagonal2(row, col, board), score)

        return score

    def score_diagonal1(self, row, col, board):
        # starting top left and going to bottom right
        score = 1

        base_color = board[row][col]
        streak_plus = True
        streak_minus = True

        for n in range(1, 7):
            if row + n < 6 and col + n < 7 and streak_plus:
                if board[row + n][col + n] == base_color:
                    score += 1
                else:
                    streak_plus = False

            if row - n >= 0 and col - n >= 0 and streak_minus:
                if board[row - n][col - n] == base_color:
                    score += 1
                else:
                    streak_minus = False

        return score

    def score_diagonal2(self, row, col, board):
        # starting top right and going to bottom left
        score = 1

        base_color = board[row][col]
        streak_plus = True
        streak_minus = True

        for n in range(1, 7):
            if row + n < 6 and col - n >= 0 and streak_plus:
                if board[row + n][col - n] == base_color:
                    score += 1
                else:
                    streak_plus = False

            if row - n >= 0 and col + n < 7 and streak_minus:
                if board[row - n][col + n] == base_color:
                    score += 1
                else:
                    streak_minus = False

        return score

    def score_horizontal(self, row, col, board):
        score = 1

        base_color = board[row][col]
        streak_plus = True
        streak_minus = True

        for c in range(1, 7):
            if col + c < 7 and streak_plus:
                if board[row][col + c] == base_color:
                    score += 1
                else:
                    streak_plus = False

            if col - c >= 0 and streak_minus:
                if board[row][col - c] == base_color:
                    score += 1
                else:
                    streak_minus = False

        return score

    def score_vertical(self, row, col, board):
        score = 1
        streak_plus = True
        streak_minus = True
        base_color = board[row][col]

        for r in range(1, 6):
            if row + r < 6 and streak_plus:
                if board[row + r][col] == base_color:
                    score += 1
                else:
                    streak_plus = False

            if row - r >= 0 and streak_minus:
                if board[row - r][col] == base_color:
                    score += 1
                else:
                    streak_minus = False

        return score

    def update(self):

        # check for an escape press
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"
            # self.game.scene_pop = True
            return

        self.check_winner()
        if self.game.winner is not None:
            self.game.scene_push = "FourJacksGameOver"

        if self.game.four_jacks_ai == self.current_turn:
            self.update_ai_turn()
        else:
            self.update_player_turn()

        # modulo are turn and column so they wrap around
        self.selected_column = self.selected_column % 7
        self.current_turn = self.current_turn % 2

    def draw(self):
        self.game.screen.fill((80, 80, 80))

        # draw the game board
        self.board.fill((33, 33, 255))
        for row in range(6):
            for col in range(7):
                if self.board_map[row][col] != 0:
                    pygame.draw.circle(
                        self.board,
                        self.board_map[row][col],
                        (50 * col + 50, 40 * row + 40),
                        18,
                    )
                else:
                    pygame.draw.circle(
                        self.board, self.key_color, (50 * col + 50, 40 * row + 40), 18
                    )

        # check if this is an ai match
        if self.game.four_jacks_ai is not None:
            # check if the ai is thinking and overlay the thinking text
            if self.game.four_jacks_ai == self.current_turn:
                thinking_text = self.standard_text("AI is thinking...")
                # rotate text 90 degrees
                thinking_text = pygame.transform.rotate(thinking_text, 90)

                self.screen.blit(thinking_text, (0, 0))

        if settings.DEBUG:
            self.game.debug_scene.data = []
            self.game.debug_scene.data.append("Current Turn: " + str(self.current_turn))
            self.game.debug_scene.data.append(
                "AI Easy: " + str(self.game.four_jacks_easy)
            )
            self.game.debug_scene.data.append(str(self.summarize_board(self.board_map)))

            for row in range(6):
                for col in range(7):
                    if self.board_score[row][col] != 0:
                        # make text of the score
                        text = self.make_text(
                            str(self.board_score[row][col]), (255, 255, 255), 16
                        )

                        # overlay the score onto the board
                        self.board.blit(text, (50 * col + 40, 40 * row + 35))

        # overlay the game board onto the screen
        self.blit_centered(self.board, self.game.screen, (0.5, 0.56))

        # draw a piece hovering over the selected column while active
        if self.active:

            pygame.draw.circle(
                self.game.screen,
                self.colors[self.current_turn],
                (50 * self.selected_column + 170, 32),
                18,
            )
