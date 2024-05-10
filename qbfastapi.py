from fastapi import FastAPI
import scenes.quadblox.scripts.qb as qb

app = FastAPI()

@app.get("/")
def read_root():
    return {"active_games": len(games)}

@app.get("/games")
def read_boards():
    return games

@app.get("/games/{game_id}/sit")
def seat(game_id: int):
    # check for a valid game
    if game_id >= len(games):
        return "Invalid game id"

    # check for an open seat
    for i in range(len(games[game_id])):
        if games[game_id][i].dead():
            # make a new board for the player
            games[game_id][i] = qb.Board()
            games[game_id][i].clear()
            return {'seat': i}

@app.get("/games/new")
def new_board():
    create_new_board()
    return {'status': 'ok', 'game': len(games) - 1}

@app.get("/games/{game_id}")
def read_board(game_id: int):
    board_states = []
    for board in games[game_id]:
        board_states.append(board.export_board())
    return board_states

@app.post("/games/update/{game_id}/{board_number}")
def update_board(game_id: int, board_number: int, board_state: str):
    # pick a random board to update
    # board = random.choice(boards[game_id])
    games[game_id][board_number].import_board(board_state)
    return {'status': 'ok'}

@app.post("/games/line-clear-attack/{game_id}/{board_number}/{lines}")
def attack_board(game_id: int, board_number: int, lines: int):
    for i in range(9):
        if i != board_number:
            games[game_id][i].attacks_waiting += lines

    attacks_waiting = []

    for board in games[game_id]:
        attacks_waiting.append(board.attacks_waiting)

    return attacks_waiting

@app.get("/games/get-attacks/{game_id}/{board_number}")
def get_attacks(game_id: int, board_number: int):
    n = games[game_id][board_number].attacks_waiting
    games[game_id][board_number].attacks_waiting -= n
    return {'lines': n}

def create_new_board():
    new_game = []
    for _ in range(9):
        new_game.append(qb.Board())

    games.append(new_game)

games = []
create_new_board()
