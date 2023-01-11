Feature: Combinations

	Scenario Outline: Combinations scores
		Given the dices rolled <dices>
		Then the <combination> score is <score>

		Examples: Aces
			| combination     | dices     | score |
			| Aces            | 2 2 3 4 5 | 0     |
			| Aces            | 1 2 3 4 5 | 1     |
			| Aces            | 1 1 1 1 1 | 5     |

		Examples: Twos
			| combination     | dices     | score |
			| Twos            | 2 2 3 4 5 | 4     |
			| Twos            | 1 2 3 4 5 | 2     |

		Examples: Threes
			| combination     | dices     | score |
			| Threes          | 2 2 3 4 5 | 3     |
			| Threes          | 3 3 3 3 3 | 15    |

		Examples: Fours
			| combination     | dices     | score |
			| Fours           | 2 2 3 4 5 | 4     |
			| Fours           | 1 2 4 4 5 | 8     |

		Examples: Fives
			| combination     | dices     | score |
			| Fives           | 2 2 3 4 4 | 0     |
			| Fives           | 1 2 3 4 5 | 5     |

		Examples: Sixes
			| combination     | dices     | score |
			| Sixes           | 2 2 3 4 5 | 0     |
			| Sixes           | 1 6 6 4 5 | 12    |

		Examples: Three Of A Kind
			| combination     | dices     | score |
			| Three Of A Kind | 1 2 3 4 5 | 0     |
			| Three Of A Kind | 2 2 3 4 5 | 0     |
			| Three Of A Kind | 1 1 1 1 1 | 5     |
			| Three Of A Kind | 3 3 3 1 1 | 11    |

		Examples: Four Of A Kind
			| combination     | dices     | score |
			| Four Of A Kind  | 1 2 3 4 5 | 0     |
			| Four Of A Kind  | 2 2 3 4 5 | 0     |
			| Four Of A Kind  | 3 3 3 1 1 | 0     |
			| Four Of A Kind  | 3 3 3 3 1 | 13    |
			| Four Of A Kind  | 1 1 1 1 1 | 5     |

		Examples: Full House
			| combination     | dices     | score |
			| Full House      | 1 2 3 4 5 | 0     |
			| Full House      | 2 2 3 4 5 | 0     |
			| Full House      | 3 3 3 1 1 | 25    |
			| Full House      | 3 3 3 3 1 | 0     |
			| Full House      | 1 1 1 1 1 | 25    |

		Examples: Yahtzee
			| combination     | dices     | score |
			| Yahtzee         | 1 2 3 4 5 | 0     |
			| Yahtzee         | 3 3 3 3 1 | 0     |
			| Yahtzee         | 3 3 3 3 3 | 50    |

		Examples: Small Straight
			| combination     | dices     | score |
			| Small Straight  | 1 2 3 4 5 | 20    |
			| Small Straight  | 1 1 2 3 4 | 20    |
			| Small Straight  | 2 2 5 3 4 | 20    |
			| Small Straight  | 6 5 4 3 6 | 20    |
			| Small Straight  | 6 5 4 6 6 | 0     |

		Examples: Large Straight
			| combination     | dices     | score |
			| Large Straight  | 1 2 3 4 5 | 40    |
			| Large Straight  | 1 1 2 3 4 | 0     |
			| Large Straight  | 2 2 5 3 4 | 0     |
			| Large Straight  | 6 5 4 3 2 | 40    |
			| Large Straight  | 6 5 4 6 6 | 0     |

		Examples: Chance
			| combination     | dices     | score |
			| Chance          | 1 2 3 4 5 | 15    |
			| Chance          | 6 6 6 6 6 | 30    |
