#!/usr/bin/env python3

import json
import os

from py2j import parse_f
from termcolor import colored

ROOT = os.path.dirname(os.path.realpath(__file__)) + "/test/"

def main():

	passed = 0
	total = 0

	for yml in sorted([ROOT+f for f in os.listdir(ROOT) if f.endswith(".yml")]):

		print(f":: Testing {yml}... ", end="")
		result = parse_f(yml)

		with open(yml[:-4] + ".json", "r") as f:
			expected = f.read()

		if result != expected:

			print(colored("failed.", "red"))
			print("-- EXPECTED --")
			print(expected)
			print("-- RESULT --")
			print(result)

		else:
			print(colored("passed.", "green"))
			passed += 1

		total += 1

	print(f":: Passed {passed}/{total}.")

if __name__ == "__main__":
	main()
