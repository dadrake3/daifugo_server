import os

API_KEY = os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")

UP = True
DOWN = False

SUITS = ["Heart", "Diamond", "Spade", "Club"]

RANKS = {
    "2": 12,
    "Ace": 11,
    "King": 10,
    "Queen": 9,
    "Jack": 8,
    "10": 7,
    "9": 6,
    "8": 5,
    "7": 4,
    "6": 3,
    "5": 2,
    "4": 1,
    "3": 0,
}


PLAYER_TABLE = "daifugo_api_player_table"
GAME_TABLE = "daifugo_api_game_table"
HAND_TABLE = "daifugo_api_hand_table"
STATE_TABLE = "daifugo_api_state_table"

HTTP_HEADERS = {
    "Content-Type": "application/graphql",
    "x-api-key": API_KEY,
    "cache-control": "no-cache",
}
