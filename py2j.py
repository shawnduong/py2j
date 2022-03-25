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
		return [
			{"data": l.split("#")[0], "indent": INDENT(l)}
			for l in yaml.split("\n")
		]

	def parse(self, start: int, stop: int) -> Union[dict, list]:
		"""
		Recursive YAML parsing algorithm runs on self.yaml from [start, stop)
		and returns either a dict or a list depending on the content.
		"""

		# Output is a dictionary by default, but may change to a list later.
		output = {}

		# Iterate from [start. stop)
		i = start
		while i < stop:

			line = self.yaml[i]["data"]

			# Stub.
			if False:
				pass

			# Basic association.
			elif ": " in line:
				k, v = self.association(i)
				output[k] = v

			# Move to the next line.
			i += 1

		return output

	def association(self, line: int) -> tuple:
		"""
		Basic association given a line number returns key, value.
		"""

		tokens = self.yaml[line]["data"].split(": ")

		key = self.strip(tokens[0])
		value = self.strip(": ".join(tokens[1::]))

		return key, value

	def strip(self, s: str) -> str:
		"""
		Strip a string s of excess whitespace and existing quote pairs.
		"""

		s = s.lstrip().rstrip()

		if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
			s = s[1:-1]

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

