#!/usr/bin/env python3

import json
import os

from py2j import parse_f
from termcolor import colored

def test(name: str, path: str):
	"""
	Run all test cases within a given directory. Test cases should end in
	".yml" and their expected outputs should be in the same directory and end
	in ".json"
	"""

	if not os.path.exists(path):
		return

	passed = 0
	total = 0

	print(f"-- SET: {name} --")

	for yml in sorted([path+f for f in os.listdir(path) if f.endswith(".yml")]):

		result = parse_f(yml)

		with open(yml[:-4] + ".json", "r") as f:
			expected = f.read()

		if result != expected:

			print(":: %s: " % colored("FAIL", "red"), end="")
			print("-- EXPECTED --")
			print(expected)
			print("-- RESULT --")
			print(result)

		else:
			print(":: %s: " % colored("PASS", "green"), end="")
			passed += 1

		print(yml.split("/")[-1][:-4])

		total += 1

	print(f":: Passed {passed}/{total}.")

def main():

	# Run included and proprietary test cases.
	root = os.path.dirname(os.path.realpath(__file__)) + "/test/"
	secret = root + "secret/"

	test("STANDARD", root)
	test("PROPRIETARY", secret)

if __name__ == "__main__":
	main()
