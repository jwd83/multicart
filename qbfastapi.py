from fastapi import FastAPI
import scenes.quadblox.scripts.qb as qb
import random
app = FastAPI()

@app.get("/")
def read_root():
    return {"active_games": len(boards)}

@app.get("/boards")
def read_boards():
    return boards

@app.get("/boards/new")
def new_board():
    create_new_board()
    return len(boards) - 1

@app.get("/boards/{game_id}")
def read_board(game_id: int):
    board_states = []
    for board in boards[game_id]:
        board_states.append(board.export_board())
    return board_states

@app.post("/boards/update/{game_id}")
def update_board(game_id: int, board_state: str):
    # pick a random board to update
    board = random.choice(boards[game_id])
    board.import_board(board_state)

    return boards[game_id]


def create_new_board():
    new_game = []
    for _ in range(9):
        new_game.append(qb.Board())

    boards.append(new_game)

boards = []
create_new_board()
