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

		# Tracker variable for whether or not l is within a ">" or "|"
		inMultiLine, indentation = False, None

		# [{"data": content, "indent": INDENT(content)}, ...]
		output = []
		for l in yaml.split("\n"):

			# Read the line into a dictionary.
			line = {"data": l.split("#")[0], "indent": INDENT(l)}
			l = self.strip(line["data"])

			# Escape multi-line.
			if inMultiLine and 0 < line["indent"] <= indentation:
				inMultiLine, indentation = False, None

			# Preserve empty lines in multi-line strings.
			if l.endswith(">") or l.endswith("|"):
				inMultiLine, indentation = True, line["indent"]

			# Exclude empty lines and document headers.
			if inMultiLine or (len(l) > 0 and not l.startswith("---")):
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

			# Multi-line string.
			if l.endswith("|") or l.endswith(">"):

				# Read the lines and skip over them.
				string, n = self.multi_line(i)
				output.update(string)
				i += n
				continue

			# Block association means a recursive call.
			elif (i+1 < stop and self.yaml[i]["indent"] < self.yaml[i+1]["indent"]
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

			# List item means a recursive call.
			elif l.startswith("- "):

				# Remove the excess whitespace and hyphen from the line.
				self.yaml[i]["data"] = self.strip(l[2:])
				self.yaml[i]["indent"] += 2

				j = i

				# Find the recursive range's end.
				for j in range(i+1, stop):
					if self.yaml[j]["indent"] < self.yaml[i]["indent"]:
						break

				# Change the output type to a list if it isn't already.
				if type(output) is dict:
					output = []

				# Single list item.
				if j <= i+1:
					output.append(self.yaml[i]["data"])

				# Block list item.
				else:
					item = self.parse(i, j)
					output.append(item)
					i = j
					continue

			# Inline list item.
			elif l.startswith("["):
				output = [self.strip(i) for i in l.strip("[]").split(",")]

			# Inline associations.
			elif l.startswith("{"):
				output = self.inline_association(i)

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

		# Inline list item.
		if str(value).startswith("["):
			value = [self.strip(i) for i in value.strip("[]").split(",")]

		return key, value

	def inline_association(self, index: int) -> dict:
		"""
		Inline association given a line index returns a dict of key:value.
		"""

		output = {}
		lines = self.strip(self.yaml[index]["data"][1:-1]).split(",")

		for line in lines:
			tokens = line.split(": ")
			output[self.strip(tokens[0])] = self.strip(": ".join(tokens[1::]))

		return output

	def multi_line(self, index: int) -> tuple:
		"""
		Multi-line string reads starting from the index of the key, and returns
		{key:string}, n where n is the number of string lines read.
		"""

		# ">" means don't preserve newlines, while "|" means preserve.
		if self.strip(self.yaml[index]["data"]).endswith(">"):
			preserve = False
		else:
			preserve = True

		string = ""

		# Read the multi-line string.
		for i in range(index+1, len(self.yaml)):

			# Break upon unindenting.
			if self.yaml[i]["indent"] <= self.yaml[index]["indent"]:

				blankText = False

				# Make sure that this isn't just a blank line in a text.
				for j in range(i, len(self.yaml)):
					if self.yaml[j]["indent"] >= self.yaml[index+1]["indent"]:
						blankText = True
						break

				# Exit the loop with i at the last line.
				if not blankText:
					i -= 1
					break

				# Strip the last space and replace it with a newline.
				else:
					string = string[:-1] + "\n"
					continue

			string += " " * (self.yaml[i]["indent"] - self.yaml[index+1]["indent"])
			string += self.strip(self.yaml[i]["data"], preserveQuotes=True)

			if preserve:
				string += "\n"
			else:
				string += " "

		string = string[:-1] + "\n"

		return {"data": string}, i - index

	def strip(self, s: str, preserveQuotes: bool=False) -> Union[str, int, bool]:
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
		if preserveQuotes:
			pass
		elif (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
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

