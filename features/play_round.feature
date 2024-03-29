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

	Scenario: Bob cannot score if he didn't roll the dices
		When Bob scores the Chance line
		Then an error said "You must roll the dices first"

	Scenario: Bob can keep some dices aside before rerolling
		When Bob rolls the dices
		And Bob keeps the dices 1, 2 and 3
		And Bob rerolls the dices
		Then dices 1, 2 and 3 have the same value as before
		And dices 4 and 5 are on the track

	Scenario: Bob can roll dices 3 times
		When Bob rolls the dices
		And Bob rerolls the dices
		And Bob rerolls the dices
		Then there was no error

	Scenario: Bob can not roll dices more than 3 times
		When Bob rolls the dices
		And Bob rerolls the dices
		And Bob rerolls the dices
		And Bob rerolls the dices
		Then an error said "You already rolled the dices 3 times"

	Scenario: Alice played the last round and the game is over
		When the last round is played
		Then the game is over
