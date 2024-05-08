from fastapi import FastAPI
import scenes.quadblox.scripts.qb as qb

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
    return boards[game_id]

@app.post("/boards")
def update_board(game_id: int, owner: int, board: list):
    return boards[game_id]


def create_new_board():
    new_game = []
    for _ in range(9):
        new_game.append(qb.Board())

    boards.append(new_game)

boards = []
create_new_board()
