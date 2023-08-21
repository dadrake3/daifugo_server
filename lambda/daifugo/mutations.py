from collections import namedtuple

Mutation = namedtuple("Mutation", ["name", "value"])

UPDATE_HAND_MUTATION = Mutation(
    "updateHand",
    """
    mutation UpdateHand($id: ID!, $cards: [String]!) {
        updateHand(id: $id, cards: $cards) {
            id
            cards
        }
    }
""",
)

CREATE_HAND_MUTATION = Mutation(
    "createHand",
    """
    mutation CreateHand {
        createHand {
            id
            cards
        }
    }
""",
)

CREATE_PLAYER_MUTATION = Mutation(
    "createPlayer",
    """
    mutation CreatePlayer($game_id: String!, $name: String!, $hand_id: String!) {
        createPlayer(game_id: $game_id, name: $name, hand_id: $hand_id) {
            id
            name
            game_id
            hand_id
            rank
            has_passed
        }
    }
""",
)

UPDATE_GAME_MUTATION = Mutation(
    "updateGame",
    """
    mutation UpdateGame($id: ID!, $players: [String], $joinable: Boolean) {
        updateGame(id: $id, players: $players, joinable: $joinable) {
            id
            joinable
            players
            state_id
        }
    }
""",
)

UPDATE_PLAYER_MUTATION = Mutation(
    "updatePlayer",
    """
    mutation UpdatePlayer($id: ID!, $rank: Int, $has_passed: Boolean){
        updatePlayer(id: $id, rank: $rank, has_passed: $has_passed) {
            id
            name
            game_id
            hand_id 
            rank
            has_passed
        }
    }
""",
)


CREATE_STATE_MUTATION = Mutation(
    "createState",
    """
    mutation CreateState($game_id: String!, $active_player_id: String!, $active_player_idx: Int!){
        createState(
            game_id: $game_id, 
            active_player_id: $active_player_id, 
            active_player_idx: $active_player_idx
        ){
            id
            game_id
            active_player_idx
            active_player_id
            last_played_idx
            top_of_pile
            pot_size
            active_pattern
            revolution
            direction
        }
    }
""",
)


UPDATE_STATE_MUTATION = Mutation(
    "updateState",
    """
    mutation UpdateState(
        $id: ID!, 
        $active_player_idx
        $last_played_idx: Int
        $active_player_id: String
        $top_of_pile: [String]
        $pot_size: Int
        $active_pattern: String
        $revolution: Boolean
        $direction: Boolean
    ){
        updateState(
            id: $id
            active_player_idx: $active_player_idx
            last_played_idx: $last_played_idx
            active_player_id: $active_player_id
            top_of_pile: $top_of_pile
            pot_size: $pot_size
            active_pattern: $active_pattern
            revolution: $revolution
            direction: $direction
        ) {
            id
            game_id
            active_player_idx
            last_played_idx
            active_player_id
            top_of_pile
            pot_size
            active_pattern
            revolution
            direction
        }
    }
""",
)

CREATE_GAME_MUTATION = Mutation(
    "createGame",
    """
    mutation CreateGame {
        createGame {
            id
            joinable
            state_id
            players
        }
    }
""",
)
