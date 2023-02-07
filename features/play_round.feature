Feature: play a round
	Background: Game started with 2 players
		Given some players named
			| name  |
			| Bob   |
			| Alice |
		And the game is started

	Scenario: Alice can't play
		Given the game is started
		When Alice rolls the dices
		Then an error said "Alice, it's not your turn to play"

	Scenario: Bob can play
		When Bob rolls the dices
		And Bob scores the Chance line
		Then Bob score is positive
		And it's Alice's turn to play