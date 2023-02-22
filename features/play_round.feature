Feature: play a round
	Background: Game started with 2 players
		Given some players named
			| name  |
			| Bob   |
			| Alice |
		And the game is started

	Scenario: Alice can't play because it's not her turn
		When Alice rolls the dices
		Then an error said "Alice, it's not your turn to play"

	Scenario: Bob can play because it is his turn
		When Bob rolls the dices
		And Bob scores the Chance line
		Then Bob score is positive
		And it's Alice's turn to play

	Scenario: Bob can't score an already scored line
		Given Bob scored 4 for Aces
		When Bob rolls the dices
		And Bob scores the Aces line
		Then an error said "Bob, you already scored Aces"
