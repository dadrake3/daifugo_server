import json
import urllib3
import os


# API_KEY = "da2-mt3szhjqz5eobifgxrbh3rwtjm"
# API_URL = "https://dlrtdaba5jfgzgkos2qzg6e3bm.appsync-api.us-east-1.amazonaws.com/graphql"
API_KEY = os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")


def join_game_handler(event, context):
    """
        Creates a player and then adds them to an existing game
        
        TODO: assert that the game actually exists in dyanmo
    
    """
    game_id = event["arguments"]["game_id"]
    player_name = event["arguments"]["player_name"]
    
    http = urllib3.PoolManager()
    http_headers = {
        'Content-Type': "application/graphql",
        'x-api-key': API_KEY,
        'cache-control': "no-cache",
    }
    
    create_hand_mutation = """
        mutation CreateHand {
            createHand {
                id
                cards
            }
        }
    """
    
    create_hand_response = http.request(
        'POST',
        API_URL,
        body = json.dumps({"query": create_hand_mutation}),
        headers=http_headers,
    )
    create_hand_response = json.loads(create_hand_response.data)
    
    hand_id = create_hand_response["data"]["createHand"]["id"]
    
    
    create_player_mutation = """
        mutation CreatePlayer {{
            createPlayer(game_id: "{game_id}", name: "{player_name}", hand_id: "{hand_id}") {{
                id
                name
                game_id
                hand_id
                order
                rank
            }}
        }}
    """.format(game_id=game_id, player_name=player_name, hand_id=hand_id)
    
    create_player_response = http.request(
        'POST',
        API_URL,
        body = json.dumps({"query": create_player_mutation}),
        headers=http_headers,
    )
    create_player_response = json.loads(create_player_response.data)
    player_id = create_player_response["data"]["createPlayer"]["id"]
    
    update_game_mutation = """
        mutation UpdateGame {{
            updateGame(id: "{game_id}", players: ["{player_id}"], joinable: true) {{
                id
                joinable
                players
                state_id
            }}
        }}
    """.format(player_id=player_id, game_id=game_id)
    
    update_game_response = http.request(
        'POST',
        API_URL,
        body = json.dumps({"query": update_game_mutation}),
        headers=http_headers,
    )
    
    return create_player_response["data"]["createPlayer"]

