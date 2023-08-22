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
    mutation UpdateGame($id: ID!, $players: [String], $joinable: Boolean, $state_id: String) {
        updateGame(id: $id, players: $players, joinable: $joinable, state_id: $state_id) {
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
        $active_player_idx: Int,
        $last_played_idx: Int,
        $active_player_id: String,
        $top_of_pile: [String],
        $pot_size: Int,
        $active_pattern: String,
        $revolution: Boolean,
        $direction: Boolean
    ){
        updateState(
            id: $id,
            active_player_idx: $active_player_idx,
            last_played_idx: $last_played_idx,
            active_player_id: $active_player_id,
            top_of_pile: $top_of_pile,
            pot_size: $pot_size,
            active_pattern: $active_pattern,
            revolution: $revolution,
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


JOIN_GAME_MUTATION = Mutation(
    "joinGame",
    """
    mutation JoinGame($game_id: ID!, $player_name: String!) {
        joinGame(game_id: $game_id, player_name: $player_name) {
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


START_GAME_MUTATION = Mutation(
    "startGame",
    """
    mutation StartGame($game_id: String!) {
        startGame(game_id: $game_id) {
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


PLAY_CARDS_MUTATION = Mutation(
    "playCards",
    """
    mutation PlayCards($game_id: String!, $player_id: String!, $cards: [String]!, $discards: [String]!){
        playCards(game_id: $game_id, player_id: $player_id, cards: $cards, discards: $discards){
            id
            game_id
            active_player_idx
            active_player_id
            last_played_idx
            top_of_pile
            pot_size
            revolution
            direction
            active_pattern
        }
    }
    """,
)
