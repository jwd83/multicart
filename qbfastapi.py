from fastapi import FastAPI
import scenes.quadblox.scripts.qb as qb

app = FastAPI()

@app.get("/")
def read_root():
    return {"active_games": len(boards)}

@app.get("/games/{game_id}/sit")
def seat(game_id: int):
    # check for a valid game
    if game_id >= len(boards):
        return "Invalid game id"

    # check for an open seat
    for i in range(len(boards[game_id])):
        if boards[game_id][i].dead():
            boards[game_id][i].clear()
            return {'seat': i}

@app.get("/games")
def read_boards():
    return boards

@app.get("/games/new")
def new_board():
    create_new_board()
    return {'status': 'ok', 'game': len(boards) - 1}

@app.get("/games/{game_id}")
def read_board(game_id: int):
    board_states = []
    for board in boards[game_id]:
        board_states.append(board.export_board())
    return board_states

@app.post("/games/update/{game_id}/{board_number}")
def update_board(game_id: int, board_number: int, board_state: str):
    # pick a random board to update
    # board = random.choice(boards[game_id])
    boards[game_id][board_number].import_board(board_state)
    return {'status': 'ok'}

@app.post("/games/line-clear-attack/{game_id}/{board_number}/{lines}")
def attack_board(game_id: int, board_number: int, lines: int):
    for i in range(9):
        if i != board_number:
            boards[game_id][i].attacks_waiting += lines

    attacks_waiting = []

    for board in boards[game_id]:
        attacks_waiting.append(board.attacks_waiting)

    return attacks_waiting

@app.get("/games/get-attacks/{game_id}/{board_number}")
def get_attacks(game_id: int, board_number: int):
    n = boards[game_id][board_number].attacks_waiting
    boards[game_id][board_number].attacks_waiting -= n
    return {'lines': n}

def create_new_board():
    new_game = []
    for _ in range(9):
        new_game.append(qb.Board())

    boards.append(new_game)

boards = []
create_new_board()
