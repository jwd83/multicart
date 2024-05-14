import os

# .env support
from dotenv import load_dotenv

# fastapi
import uvicorn
from fastapi import FastAPI
import scenes.quadblox.scripts.qb as qb


# Postgres
import psycopg
from psycopg.rows import dict_row

# my custom namebuilder
import namebuilder

TIMEOUT = 30  # seconds
STARTING_LOBBY_COUNT = 3

app = FastAPI()


@app.get("/")
def read_root():
    return get_active_games()


@app.get("/leaderboard")
def read_leaderboard():
    return high_scores


@app.post("/leaderboard")
def update_leaderboard(
    player: str, time: float, lines: int, pieces: int, score: int, frames: int
):
    with psycopg.connect(conninfo=os.getenv("DATABASE")) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO
                high_scores

                (player, time, lines, pieces, score, frames)

                VALUES

                (%s, %s, %s, %s, %s, %s)

                """,
                (player, time, lines, pieces, score, frames),
            )
    refresh_high_scores()
    return high_scores


@app.get("/games")
def active_games():
    return get_active_games()


@app.get("/games/{game_id}/sit")
def seat(game_id: int):
    # check for a valid game
    if game_id >= len(games) or game_id < 0:
        return {"status": "error", "message": "Invalid game_id"}

    purge_dead_boards(game_id)

    # check for an open seat
    for i in range(len(games[game_id])):
        if games[game_id][i].dead():
            # make a new board for the player
            games[game_id][i] = qb.Board()
            games[game_id][i].clear()
            return {"status": "ok", "seat": i}

    # if no open seats return an error
    return {"status": "error", "message": "No open seats"}


@app.get("/games/new")
def new_board():
    create_new_board()
    return {"status": "ok", "game_id": len(games) - 1, "name": lobbies[-1]}


@app.get("/games/{game_id}")
def read_board(game_id: int):
    board_states = []

    purge_dead_boards(game_id)

    for board in games[game_id]:
        board_states.append(board.export_board())
    return board_states


@app.post("/games/update/{game_id}/{board_number}")
def update_board(game_id: int, board_number: int, board_state: str):
    # pick a random board to update
    # board = random.choice(boards[game_id])
    games[game_id][board_number].import_board(board_state)
    return {"status": "ok"}


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
    return {"lines": n}


def create_new_board():
    # create our list to hold our new set of boards
    new_game = []

    for _ in range(9):
        # create each board and zero out it's timeout so it's not active
        new_board = qb.Board()
        new_board.zero_timeout()
        new_game.append(new_board)

    games.append(new_game)

    lobbies.append(nb.build("ac"))


def purge_dead_boards(game_id):

    # purge any disconnected boards / dead boards
    for i in range(len(games[game_id])):
        if not games[game_id][i].dead():
            if games[game_id][i].timeout() > TIMEOUT:
                games[game_id][i] = qb.Board()


def get_active_games():
    lobby_list = []

    for i, lobby in enumerate(lobbies):
        player_count = 0
        for board in games[i]:
            if board.timeout() < TIMEOUT:
                player_count += 1

        lobby_list.append(
            {
                "game_id": i,
                "name": lobby,
                "players": player_count,
                "seats_available": 9 - player_count,
            }
        )

    return {"active_games": len(games), "lobbies": lobby_list}


def refresh_high_scores():
    global high_scores
    with psycopg.connect(conninfo=os.getenv("DATABASE"), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM high_scores ORDER BY time ASC LIMIT 10")
            high_scores = cur.fetchall()


load_dotenv()

nb = namebuilder.NameBuilder()
lobbies = []
games = []
high_scores = []

refresh_high_scores()

for _ in range(STARTING_LOBBY_COUNT):
    create_new_board()


if __name__ == "__main__":
    # bind to 8000 or use the PORT environment variable

    port = int(os.getenv("PORT", default=8000))
    print(f"Starting server on port http://localhost:{port}")
    uvicorn.run(app="qbfastapi:app", host="0.0.0.0", port=port, reload=True)
