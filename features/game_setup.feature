Feature: start a game

	Scenario: start a game with one player
		Given a player named John
		And the game is started
		Then John score is equal to 0
		And it's John's turn to play

	Scenario: start a game with two players
		Given some players named
		  | name  |
		  | Alice |
		  | Bob   |
		And the game is started
		Then Alice score is equal to 0
		And Bob score is equal to 0
		And it's Alice's turn to play

	Scenario: Same players names for the same game is not allowed
		Given some players named
		  | name  |
		  | Alice |
		  | Alice |
		And the game is started
		Then just 1 player is in the game

	Scenario: can't start a game if no player joined
		Given no player
		When the game is created
		Then the game can not be started
