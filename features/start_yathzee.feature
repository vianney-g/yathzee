Feature: start a game

	Scenario: start a game with one player
		Given a player named John
		When the game is created
		Then John score is equal to 0
		And it's John's turn to play
	
	Scenario: start a game with two players
		Given some players named
		  | name  |
		  | Alice |
		  | Bob   |
		When the game is created
		Then Alice score is equal to 0
		And Bob score is equal to 0
		And it's Alice's turn to play

	Scenario: Same players names for the same game is not allowed
		Given some players named
		  | name  |
		  | Alice |
		  | Alice |
		When the game is created
		Then an error "A player named Alice already exists" is raised
	
	Scenario: can't start a game if no player joined
		Given no player
		When the game is created
		Then an error "Can't create a game with no player" is raised
