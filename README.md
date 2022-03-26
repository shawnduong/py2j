# py2j - Python YAML to JSON

py2j is a lightweight Python library that converts YAML data to JSON. *Not to be confused with log2j, or y2k.*

**This project is currently in development.**

## Usage

Just import the library and then use `parse_f`.

```python
from py2j import parse_f

# If you want JSON.
data = parse_f("./input_file.yml")

# If you just want a regular Python dictionary.
data = parse_f("./input_file.yml", jsout=False)
```
