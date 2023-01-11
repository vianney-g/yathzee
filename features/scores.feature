Feature: Scoring

	Scenario: Upper section with bonus
		Given the following scorecard
			| category        | score |  
			| Aces            | 3     |
			| Twos            | 6     |
			| Threes          | 9     |
			| Fours           | 12    |
			| Fives           | 15    |
			| Sixes           | 18    |

		Then the total of scorecard is 98
		And the scorecard is not complete


	Scenario: Upper section without bonus
		Given the following scorecard
			| category        | score |  
			| Aces            | 2     |
			| Twos            | 6     |
			| Threes          | 9     |
			| Fours           | 12    |
			| Fives           | 15    |
			| Sixes           | 18    |

		Then the total of scorecard is 62
		And the scorecard is not complete

	Scenario: Complete sheet
		Given the following scorecard
			| category        | score |  
			| Aces            | 3     |
			| Twos            | 6     |
			| Threes          | 9     |
			| Fours           | 12    |
			| Fives           | 15    |
			| Sixes           | 18    |
		        | Three Of A Kind | 10    |
		        | Four Of A Kind  | 10    |
		        | Full House      | 25    |
		        | Small Straight  | 30    |
		        | Large Straight  | 40    |
		        | Yahtzee         | 50    |
		        | Chance          | 10    |
		        | Yahtzee Bonus   | 100   |

		Then the total of scorecard is 373
		And the scorecard is complete

