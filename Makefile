.PHONY: tests mypy

tests:
	behave

mypy:
	mypy yahtzee
