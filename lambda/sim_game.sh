#!/bin/bash

daifugo create-game
GAME_ID=...

daifugo join-game $GAME_ID "daryl"
PLAYER_ID_D=...

daifugo join-game $GAME_ID "will"
PLAYER_ID_W=...

daifugo join-game $GAME_ID "lauren"
PLAYER_ID_L=...

daifugo join-game $GAME_ID "rebers"
PLAYER_ID_R=...

daifugo start-game $GAME_ID

