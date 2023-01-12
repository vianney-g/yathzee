.PHONY: all tests mypy

all: mypy tests

tests:
	behave

mypy:
	mypy yahtzee
