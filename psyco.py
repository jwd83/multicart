# trying out psyco
import os
from dotenv import load_dotenv
import psycopg


if __name__ == "__main__":

    load_dotenv()  # take environment variables from .env.

    with psycopg.connect(conninfo=os.getenv('DATABASE')) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM high_scores")
            users = cur.fetchall()
            print(users)

