from typing import Union

INDENT = lambda s: len(s) - len(s.lstrip())

class Parser:

	yaml = None
	data = None

	def __init__(self, yaml):
		self.yaml = self.read_yaml(yaml)
		self.data = self.parse(0, len(self.yaml))

	def read_yaml(self, yaml: str) -> list:
		"""
		Take in a YAML string and output a list of only meaningful YAML data
		and the indentation level of each meaningful line.
		"""

		# [{"data": content, "indent": INDENT(content)}, ...]
		output = []
		for l in yaml.split("\n"):

			# Read the line into a dictionary.
			line = {"data": l.split("#")[0], "indent": INDENT(l)}

			# Exclude empty lines.
			if len(self.strip(line["data"])) > 0:
				output.append(line)

		# Backstop for recursion.
		output.append({"data": "", "indent": 0})

		return output

	def parse(self, start: int, stop: int) -> Union[dict, list]:
		"""
		Recursive YAML parsing algorithm runs on self.yaml from [start, stop)
		and returns either a dict or a list depending on the content.
		"""

		# Output is a dictionary by default, but may change to a list later.
		output = {}

		# Iterate from [start, stop)
		i = start
		while i < stop:

			line = self.yaml[i]["data"]
			l = self.strip(line)

			# Block association means a recursive call.
			if (i+1 < stop and self.yaml[i]["indent"] < self.yaml[i+1]["indent"]
				and not l.startswith("- ")
			):

				# Get the key name.
				key = self.strip(line.split(":")[0])

				# Find the recursive range's end.
				for j in range(i+1, stop):
					if self.yaml[j]["indent"] <= self.yaml[i]["indent"]:
						break

				# Hitting the backstop should include the last item.
				if j == stop-1:
					j += 1

				# Perform a recursive call.
				output[key] = self.parse(i+1, j)

				# Skip over the block.
				i = j
				continue

			# List item.
			elif l.startswith("- "):

				# Remove the excess whitespace and hyphen from the line.
				self.yaml[i]["data"] = self.strip(self.yaml[i]["data"])[2:]
				self.yaml[i]["indent"] += 2

				j = 0

				# Find the recursive range's end.
				for j in range(i+1, stop):
					if self.yaml[j]["indent"] < self.yaml[i]["indent"]:
						break

				# Change the output type to a list if it isn't already.
				if type(output) is dict:
					output = []

				# Single list item.
				if j == i+1:
					output.append(self.strip(l[2:]))

				# Block list item.
				else:
					item = self.parse(i, j)
					output.append(item)
					i = j
					continue

			# Basic association.
			elif ": " in line:
				k, v = self.association(i)
				output[k] = v

			# Move to the next line.
			i += 1

		return output

	def association(self, index: int) -> tuple:
		"""
		Basic association given a line index returns key, value.
		"""

		tokens = self.yaml[index]["data"].split(": ")

		key = self.strip(tokens[0])
		value = self.strip(": ".join(tokens[1::]))

		return key, value

	def strip(self, s: str) -> Union[str, int, bool]:
		"""
		Strip a string s of excess whitespace and existing quote pairs. If it
		is an int or bool, return it as such.
		"""

		s = s.lstrip().rstrip()

		# Handle booleans true/false/yes/no.
		if s.lower() == "true" or s.lower() == "yes":
			return True
		elif s.lower() == "false" or s.lower() == "no":
			return False

		# Get rid of quote pairs.
		if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
			s = s[1:-1]

		# Convert integers.
		if s.isnumeric():
			return int(s)

		return s

def parse_f(filename: str, jsout: bool=True, indent: int=4) -> Union[str, dict]:
	"""
	Parse a YAML file given the filename. If jsout=True, return JSON str output.
	Otherwise, parse_f will return a dict. If jsout=True, an indentation width
	may also be specified. This is just a wrapper for parse.
	"""

	with open(filename, "r") as f:
		yaml = f.read()

	return parse(yaml, jsout, indent)

def parse(yaml: str, jsout: bool=True, indent: int=4) -> Union[str, dict]:
	"""
	Parse a YAML string. If jsout=True, return JSON str output. Otherwise, parse
	will return a dict. If jsout=True, an indentation width may also be
	specified.
	"""

	import json

	if jsout:
		return json.dumps(Parser(yaml).data, indent=indent)
	else:
		return Parser(yaml).data

